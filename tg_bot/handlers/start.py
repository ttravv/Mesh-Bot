from aiogram import types, Router, F
from aiogram.filters import Command
from dnevniklib.errors.token import DnevnikTokenError
from dnevniklib.student.student import Student
from dnevniklib.homeworks.homeworks import Homeworks
from dnevniklib.schedule.schedule import Schedule
from dnevniklib.marks.marks import Marks, MarksByDate
from dnevniklib.marks.marksWrap import MarksWrap
from dnevniklib.homeworks.homeworksWrap import HomeworksWrap
from datetime import datetime, timedelta
from dnevniklib.notification.notification import Notification
from dnevniklib.notification.notificationWrap import NotificationWrap
import logging

from tg_bot.handlers.keyboards import create_keyboard, create_options_keyboard
from dnevniklib.calendar.calendar import Calendar

router = Router()
user_tokens = {}
user_notifications = {}
user_state = {}
logging.basicConfig(level=logging.INFO)


@router.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = create_keyboard()
    notification_message = await message.answer(
        "👋 Пожалуйста, нажмите на кнопку и войдите в аккаунт, скопируйте весь текст из куки и ответьте на это сообщение скопированным текстом.",
        reply_markup=keyboard,
    )

    user_notifications[message.from_user.id] = notification_message.message_id


@router.message(F.text)
async def process_token(message: types.Message):
    token = message.text
    chat_id = message.from_user.id

    if chat_id in user_tokens:
        await message.answer(
            "🚫 Вы уже авторизованы. Пожалуйста, используйте команду 'Обновить токен', если хотите изменить токен."
        )
        return

    user_tokens[chat_id] = token
    keyboard = create_options_keyboard()

    if chat_id in user_notifications:
        try:
            await message.bot.delete_message(chat_id, user_notifications[chat_id])
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение уведомления: {e}")
        finally:
            del user_notifications[chat_id]

    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Не удалось удалить сообщение с токеном: {e}")

    await message.answer(
        "✅ Токен успешно добавлен! Вы успешно авторизованы и можете использовать бота дальше.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "profile")
async def process_profile(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    try:
        student = Student(token)
        profile_info = (
            f"<b>👤 Имя:</b> {student.first_name or 'Не указано'}\n"
            f"<b>👥 Фамилия:</b> {student.last_name or 'Не указано'}\n"
            f"<b>🆔 Отчество:</b> {student.middle_name or 'Не указано'}\n"
            f"<b>🎂 Дата рождения:</b> {student.birthdate or 'Не указано'}\n"
            f"<b>📧 Email:</b> {student.email or 'Не указано'}\n"
            f"<b>🎓 Возраст:</b> {student.age or 'Не указано'}\n"
            f"<b>🚻 Пол:</b> {'Мужской' if student.sex == 'male' else 'Женский'}\n"
            f"<b>🏫 Класс:</b> {student.class_name or 'Не указано'}\n"
            f"<b>📚 ID студента:</b> {student.id or 'Не указано'}\n"
            f"<b>🏢 ID школы:</b> {student.school_id or 'Не указано'}\n"
            f"<b>🔑 Логин:</b> {student.login or 'Не указано'}"
        )
        await callback_query.message.answer(profile_info, parse_mode="HTML")
    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен {token} недействителен.")
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error(f"Произошла ошибка при получении профиля студента: {str(e)}")
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении профиля студента: {str(e)}"
        )


@router.callback_query(F.data == "schedule")
async def process_schedule(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        process_schedule,
        action="schedule",
        user_state=user_state,
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


@router.callback_query(F.data.startswith("date_"))
async def process_date_selection(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    year, month, day = map(int, callback_query.data.split("_")[1:])
    selected_date = datetime(year, month, day)

    if user_state["action"] == "homework":
        await fetch_homework(callback_query, selected_date, token)

    if user_state["action"] == "marks_by_date":
        await fetch_marks_by_date(callback_query, selected_date, token)

    if user_state["action"] == "notifications":
        await fetch_notifications(callback_query, selected_date, token)

    if chat_id in user_state and "start_date" not in user_state[chat_id]:
        user_state[chat_id]["start_date"] = selected_date
        await callback_query.message.answer(
            "📅 Начальная дата выбрана. Теперь выберите конечную дату:"
        )

        calendar_instance = Calendar(
            chat_id,
            callback_query.message.message_id,
            process_date_selection,
            action="marks",
            user_state=user_state,
        )
        await calendar_instance.on_date(selected_date)

        msg_text, markup = await calendar_instance.setup_buttons()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)

    elif (
        chat_id in user_state
        and "start_date" in user_state[chat_id]
        or user_state["action"] == "marks"
    ):
        start_date = user_state[chat_id]["start_date"]
        end_date = selected_date

        del user_state[chat_id]

        await fetch_marks(callback_query, chat_id, start_date, end_date)

    else:
        calendar_instance = Calendar(
            chat_id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        await calendar_instance.on_date(selected_date)

        if user_state["action"] == "schedule":
            await fetch_schedule(
                callback_query, calendar_instance.date1, selected_date, token
            )
        else:
            msg_text, markup = await calendar_instance.setup_buttons()
            await callback_query.message.edit_text(msg_text, reply_markup=markup)


@router.callback_query(F.data == "notifications")
async def process_notifications(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        fetch_notifications,
        action="notifications",
        user_state=user_state,
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


async def fetch_notifications(
    callback_query: types.CallbackQuery, selected_date, token
):
    loading_message = await callback_query.message.answer("⏳ Получение уведомлений...")
    try:
        student = Student(token)
        notifications = Notification(student)
        notification_list = notifications.get_notification_by_date()

        await loading_message.delete()

        if not notification_list:
            await callback_query.message.answer("❌ Нет уведомлений на этот день.")
            return

        notifications_info = NotificationWrap.build(notification_list)

        await callback_query.message.answer(
            f"<b>📚 Уведомления на {selected_date}:\n{notifications_info}</b>",
            parse_mode="HTML",
        )

    except DnevnikTokenError:
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception:
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении уведомлений."
        )


async def fetch_schedule(callback_query, start_date, end_date, token):
    loading_message = await callback_query.message.answer("⏳ Получение расписания...")

    try:
        student = Student(token)
        schedule = Schedule(student)

        schedule_entities = []
        current_date = start_date
        while current_date <= end_date:
            schedule_entity = schedule.get_schedule_by_date(
                current_date.strftime("%Y-%m-%d")
            )
            schedule_entities.append(schedule_entity)

            current_date += timedelta(days=1)

        await loading_message.delete()

        if not schedule_entities:
            await callback_query.message.answer(
                "❌ Нет занятий в выбранном диапазоне дат."
            )
            return

        formatted_schedule = "\n\n".join(
            f"{entity.date}:\n{str(entity)}" for entity in schedule_entities
        )
        await callback_query.message.answer(formatted_schedule, parse_mode="HTML")

    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен {token} недействителен.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error(f"Произошла ошибка при получении расписания: {str(e)}")
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении расписания: {str(e)}"
        )


@router.callback_query(F.data == "homework")
async def process_homework(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        fetch_homework,
        action="homework",
        user_state=user_state,
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


async def fetch_homework(callback_query, selected_date, token):
    loading_message = await callback_query.message.answer(
        "⏳ Получение домашнего задания..."
    )
    try:
        student = Student(token)
        homeworks = Homeworks(student)
        homework_list = homeworks.get_homework_by_date(
            selected_date.strftime("%Y-%m-%d")
        )

        await loading_message.delete()

        if not homework_list:
            await callback_query.message.answer("❌ Нет домашних заданий на этот день.")
            return

        homework_info = HomeworksWrap.build(homework_list)

        await callback_query.message.answer(
            f"<b>📚 Домашние задания на {selected_date}:\n{homework_info}</b>",
            parse_mode="HTML",
        )

    except DnevnikTokenError:
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении домашнего задания: {str(e)}"
        )


@router.callback_query(F.data == "marks_by_date")
async def process_marks_by_date(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        fetch_marks,
        action="marks_by_date",
        user_state=user_state,
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


async def fetch_marks_by_date(
    callback_query: types.CallbackQuery, selected_date: datetime, token: str
):
    loading_message = await callback_query.message.answer("⏳ Получение оценок...")

    try:
        student = Student(token)
        marks_by_date_instance = MarksByDate(student)

        marks_info = marks_by_date_instance.get_mark_for_date(
            selected_date.strftime("%Y-%m-%d")
        )

        await loading_message.delete()
        await callback_query.message.answer(marks_info, parse_mode="HTML")

    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен {token} недействителен.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error(f"Произошла ошибка при получении оценок: {str(e)}")
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении оценок: {str(e)}"
        )


@router.callback_query(F.data == "marks")
async def process_marks(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    user_state[chat_id] = {}

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        process_date_selection,
        action="marks",
        user_state=user_state,
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


async def fetch_marks(
    callback_query: types.CallbackQuery, chat_id, start_date, end_date
):
    loading_message = await callback_query.message.answer("⏳ Получение оценок...")
    token = user_tokens.get(chat_id)

    try:
        student = Student(token)
        marks_instance = Marks(student)

        marks_list = marks_instance.get_marks_by_date(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
        await loading_message.delete()

        if not marks_list:
            await callback_query.message.answer("❌ Нет оценок на выбранные даты.")
            return

        marks_info = MarksWrap.build(marks_list)

        await callback_query.message.answer(
            f"📝 Оценки с [{start_date.strftime('%Y-%m-%d')}] по [{end_date.strftime('%Y-%m-%d')}]:\n{marks_info}",
            parse_mode="HTML",
        )

    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен {token} недействителен.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error(f"Произошла ошибка при получении оценок: {str(e)}")
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении оценок: {str(e)}"
        )


@router.callback_query(F.data == "cal:left")
async def process_prev_month(callback_query: types.CallbackQuery):
    try:
        calendar_instance = Calendar(
            callback_query.from_user.id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        msg_text, markup = await calendar_instance.backward()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при переключении на предыдущий месяц: {str(e)}")
        await callback_query.message.answer("❌ Ошибка при переключении месяца.")


@router.callback_query(F.data == "cal:right")
async def process_next_month(callback_query: types.CallbackQuery):
    try:
        calendar_instance = Calendar(
            callback_query.from_user.id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        msg_text, markup = await calendar_instance.forward()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при переключении на следующий месяц: {str(e)}")
        await callback_query.message.answer("❌ Ошибка при переключении месяца.")


@router.callback_query(F.data == "cal:current_month")
async def process_current_month(callback_query: types.CallbackQuery):
    try:
        calendar_instance = Calendar(
            callback_query.from_user.id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        msg_text, markup = await calendar_instance.go_to_current_month()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при переключении на текущий месяц: {str(e)}")
        await callback_query.message.answer(
            "❌ Ошибка при переключении на текущий месяц."
        )


@router.callback_query(F.data == "cal:close")
async def close_calendar(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()

        chat_id = callback_query.from_user.id

        if chat_id in user_notifications:
            try:
                await callback_query.bot.delete_message(
                    chat_id, user_notifications[chat_id]
                )
            except Exception as e:
                logging.error(f"Не удалось удалить сообщение с меню: {e}")
            else:
                del user_notifications[chat_id]

        keyboard = create_options_keyboard()
        await callback_query.message.answer(
            "❌ Календарь закрыт. Выберите опцию:", reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при закрытии календаря: {str(e)}")
        await callback_query.message.answer("❌ Ошибка при закрытии календаря.")


@router.callback_query(F.data == "refresh_token")
async def refresh_token(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id

    if chat_id in user_notifications:
        try:
            await callback_query.bot.delete_message(
                chat_id, user_notifications[chat_id]
            )
        except Exception as e:
            logging.error(
                f"Не удалось удалить сообщение уведомления при обновлении токена: {e}"
            )
        finally:
            del user_notifications[chat_id]

    user_tokens.pop(chat_id, None)

    request_message = await callback_query.message.answer(
        "🔄 Чтобы обновить токен, пожалуйста, нажмите на кнопку ниже, чтобы авторизоваться заново."
    )

    keyboard = create_keyboard()
    token_message = await callback_query.message.answer(
        "👤 Авторизуйтесь, нажав на кнопку:", reply_markup=keyboard
    )

    user_notifications[chat_id] = (request_message.message_id, token_message.message_id)

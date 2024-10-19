from aiogram import types, Router, F
from dnevniklib.calendar.calendar import Calendar
from dnevniklib.errors.token import DnevnikTokenError
from dnevniklib.student.student import Student
from dnevniklib.homeworks.homeworks import Homeworks
from dnevniklib.homeworks.homeworksWrap import HomeworksWrap
from tg_bot.global_state import (
    get_user_tokens,
    get_user_state
)


router = Router()


@router.callback_query(F.data == "homework")
async def process_homework(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    token = get_user_tokens().get(chat_id) 

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
        user_state=get_user_state()
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
    except Exception:
        await loading_message.delete()
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении домашнего задания."
        )

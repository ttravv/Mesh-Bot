from aiogram import types, Router, F
from dnevniklib.calendar.calendar import Calendar
from dnevniklib.errors.token import DnevnikTokenError
from dnevniklib.student.student import Student
from dnevniklib.marks.marks import Marks, MarksByDate
from dnevniklib.marks.marksWrap import MarksWrap
from datetime import datetime

from tg_bot.global_state import get_user_tokens, get_user_state, set_user_state
import logging

router = Router()


@router.callback_query(F.data == "marks_by_date")
async def process_marks_by_date(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_tokens = get_user_tokens()
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
        user_state=get_user_state(),
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
    except Exception:
        logging.error("Произошла ошибка при получении оценок.")
        await loading_message.delete()
        await callback_query.message.answer("❌ Произошла ошибка при получении оценок.")


@router.callback_query(F.data == "marks")
async def process_marks(callback_query: types.CallbackQuery):
    from tg_bot.handlers.date_selection import process_date_selection

    chat_id = callback_query.from_user.id
    user_tokens = get_user_tokens()
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    set_user_state(chat_id, {})

    calendar_instance = Calendar(
        chat_id,
        callback_query.message.message_id,
        process_date_selection,
        action="marks",
        user_state=get_user_state(),
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)


async def fetch_marks(
    callback_query: types.CallbackQuery, chat_id, start_date, end_date
):
    loading_message = await callback_query.message.answer("⏳ Получение оценок...")
    user_tokens = get_user_tokens()
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
            f"📝 <b>Оценки с [{start_date.strftime('%Y-%m-%d')}] по [{end_date.strftime('%Y-%m-%d')}]:\n{marks_info} </b>",
            parse_mode="HTML",
        )

    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен недействителен.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception:
        logging.error("Произошла ошибка при получении оценок.")
        await loading_message.delete()
        await callback_query.message.answer("❌ Произошла ошибка при получении оценок.")

from aiogram import types, Router, F
from dnevniklib.calendar.calendar import Calendar
from dnevniklib.student.student import Student
from dnevniklib.schedule.schedule import Schedule
from datetime import timedelta
from dnevniklib.errors.token import DnevnikTokenError
import logging
from tg_bot.global_state import (
    get_user_tokens,
    get_user_state
)

router = Router()

@router.callback_query(F.data == "schedule")
async def process_schedule(callback_query: types.CallbackQuery):
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
        process_schedule,
        action="schedule",
        user_state=get_user_state()
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)

async def fetch_schedule(callback_query: types.CallbackQuery, start_date: str, end_date: str, token: str):
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
        logging.error(f"Ошибка авторизации: токен недействителен.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error("❌ Произошла ошибка при получении расписания.")
        await loading_message.delete()
        await callback_query.message.answer(
            "❌ Произошла ошибка при получении расписания."
        )

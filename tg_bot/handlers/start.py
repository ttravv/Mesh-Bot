#ПОФИКСИТЬ УВЕДОМЛЕНИЯ, ПРИЧЕСАТЬ КОД, СДЕЛАТЬ ТАК ЧТОБЫ ДВОЙНОГО НАЖАТИЯ НЕ ТРЕБОВАЛОСЬ


from aiogram import types, Router, F
from aiogram.filters.command import Command

import logging

from tg_bot.handlers.keyboards import create_keyboard
from tg_bot.handlers.swap_calendar import (
    process_prev_month,
    process_next_month,
    process_current_month,
    close_calendar
)
from tg_bot.handlers.process_marks import (
    process_marks_by_date,
    fetch_marks_by_date,
    process_marks,
    fetch_marks
)
from tg_bot.handlers.process_homework import (
    process_homework,
    fetch_homework
)
from tg_bot.handlers.process_notifications import (
    process_notifications,
    fetch_notifications
)
from tg_bot.handlers.process_schedule import (
    fetch_schedule,
    process_schedule
)
from tg_bot.handlers.date_selection import process_date_selection
from tg_bot.handlers.profile import process_profile  # Import the profile handler
from tg_bot.handlers.token import process_token, refresh_token  # Import the token handlers

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
# Импортируем обработчики календаря
router.callback_query(F.data == "cal:left")(process_prev_month)
router.callback_query(F.data == "cal:right")(process_next_month)
router.callback_query(F.data == "cal:current_month")(process_current_month)
router.callback_query(F.data == "cal:close")(close_calendar)

# Импортируем обработчики оценок
router.callback_query(F.data == "marks_by_date")(process_marks_by_date)
router.callback_query(F.data == "marks")(process_marks)

# Импортируем обработчики домашних заданий
router.callback_query(F.data == "homework")(process_homework)

# Импортируем обработчики уведомлений
router.callback_query(F.data == "notifications")(process_notifications)

# Импортируем обработчики расписания
router.callback_query(F.data == "schedule")(process_schedule)

# Импортируем обработчики выбора даты
router.callback_query(F.data.startswith("date_"))(process_date_selection)

# Импортируем обработчик профиля
router.callback_query(F.data == "profile")(process_profile)

# Импортируем обработчики токенов
router.message(F.text)(process_token)  # Register the token handler
router.callback_query(F.data == "refresh_token")(refresh_token)  # Register the refresh token handler

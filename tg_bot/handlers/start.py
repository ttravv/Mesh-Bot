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
from tg_bot.handlers.process_marks import ( process_marks_by_date, process_marks)
from tg_bot.handlers.process_homework import process_homework
    
from tg_bot.handlers.process_notifications import process_notifications
    
from tg_bot.handlers.process_schedule import process_schedule
from tg_bot.handlers.date_selection import process_date_selection
from tg_bot.handlers.profile import process_profile  
from tg_bot.handlers.token import process_token, refresh_token  

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

router.callback_query(F.data == "cal:left")(process_prev_month)
router.callback_query(F.data == "cal:right")(process_next_month)
router.callback_query(F.data == "cal:current_month")(process_current_month)
router.callback_query(F.data == "cal:close")(close_calendar)


router.callback_query(F.data == "marks_by_date")(process_marks_by_date)
router.callback_query(F.data == "marks")(process_marks)


router.callback_query(F.data == "homework")(process_homework)

router.callback_query(F.data == "notifications")(process_notifications)


router.callback_query(F.data == "schedule")(process_schedule)


router.callback_query(F.data.startswith("date_"))(process_date_selection)


router.callback_query(F.data == "profile")(process_profile)


router.message(F.text)(process_token)  
router.callback_query(F.data == "refresh_token")(refresh_token)  

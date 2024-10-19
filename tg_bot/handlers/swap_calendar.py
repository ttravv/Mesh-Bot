from aiogram import types
from dnevniklib.calendar.calendar import Calendar

from tg_bot.handlers.keyboards import create_options_keyboard
import logging
from tg_bot.global_state import (
    get_user_state,
    get_user_notifications,
    set_user_notification
)

async def process_prev_month(callback_query: types.CallbackQuery):
    from tg_bot.handlers.date_selection import process_date_selection
    try:
        user_state = get_user_state()  
        calendar_instance = Calendar(
            callback_query.from_user.id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        msg_text, markup = await calendar_instance.backward()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)
    except Exception:
        logging.error(f"❌ Ошибка при переключении на предыдущий месяц")
        await callback_query.message.answer("❌ Ошибка при переключении месяца.")

async def process_next_month(callback_query: types.CallbackQuery):
    from tg_bot.handlers.date_selection import process_date_selection
    try:
        user_state = get_user_state()
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
        logging.error("❌ Ошибка при переключении на следующий месяц. Пожалуйста, попробуйте позже.")
        await callback_query.message.answer("❌ Ошибка при переключении месяца.")

async def process_current_month(callback_query: types.CallbackQuery):
    from tg_bot.handlers.date_selection import process_date_selection
    try:
        user_state = get_user_state()
        calendar_instance = Calendar(
            callback_query.from_user.id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        msg_text, markup = await calendar_instance.go_to_current_month()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)
    except Exception:
        logging.error(f"❌ Ошибка при переключении на текущий месяц.")
        await callback_query.message.answer("❌ Ошибка при переключении на текущий месяц.")

async def close_calendar(callback_query: types.CallbackQuery):
    
    try:
        await callback_query.message.delete()
        chat_id = callback_query.from_user.id

        user_notifications = get_user_notifications() 
        if chat_id in user_notifications:
            try:
                await callback_query.bot.delete_message(
                    chat_id, user_notifications[chat_id]
                )
            except Exception:
                logging.error("❌ Не удалось удалить сообщение с меню.")
            else:
                set_user_notification(chat_id, None) 

        keyboard = create_options_keyboard()
        await callback_query.message.answer(
            "❌ Календарь закрыт. Выберите опцию:", reply_markup=keyboard
        )
    except Exception:
        logging.error(f"❌ Ошибка при закрытии календаря.")
        await callback_query.message.answer("❌ Ошибка при закрытии календаря.")

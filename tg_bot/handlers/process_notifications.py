from aiogram import types, Router, F
from dnevniklib.calendar.calendar import Calendar
from dnevniklib.notification.notification import Notification
from dnevniklib.notification.notificationWrap import NotificationWrap
from dnevniklib.errors.token import DnevnikTokenError
from dnevniklib.student.student import Student
from tg_bot.global_state import (
    get_user_tokens,
    get_user_state,
)

router = Router()

@router.callback_query(F.data == "notifications")
async def process_notifications(callback_query: types.CallbackQuery):
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
        fetch_notifications,
        action="notifications",
        user_state=get_user_state()
    )
    msg_text, markup = await calendar_instance.setup_buttons()
    await callback_query.message.answer(msg_text, reply_markup=markup)

async def fetch_notifications(callback_query: types.CallbackQuery, selected_date, token):
    loading_message = await callback_query.message.answer("⏳ Получение уведомлений...")
    try:
        student = Student(token)
        notifications = Notification(student)
        notification_list = notifications.get_notification_by_date(selected_date.strftime("%Y-%m-%d"))

        await loading_message.delete()

        if not notification_list:
            await callback_query.message.answer("❌ Нет непрочитанных уведомлений на этот день.")
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

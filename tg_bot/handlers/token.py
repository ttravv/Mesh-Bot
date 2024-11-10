from aiogram import types, Router, F
from tg_bot.handlers.keyboards import create_keyboard, create_options_keyboard
from tg_bot.global_state import (
    set_user_token,
    remove_user_token,
    set_user_notification,
    remove_user_notification,
    get_user_tokens,
    get_user_notifications,
)
import logging
import base64

router = Router()


def is_valid_jwt(token: str) -> bool:
    parts = token.split(".")
    if len(parts) != 3:
        return False
    for part in parts:
        try:
            base64.b64decode(part + "==")
        except Exception:
            return False
    return True


@router.message(F.text)
async def process_token(message: types.Message):
    token = message.text.strip()
    chat_id = message.from_user.id
    user_tokens = get_user_tokens()

    if chat_id in user_tokens and is_valid_jwt(token):
        await message.answer(
            "🚫 Вы уже авторизованы. Пожалуйста, используйте команду 'Обновить токен', если хотите изменить токен."
        )
        return

    if not is_valid_jwt(token):
        await message.answer(
            "🚫 Токен некорректен. Пожалуйста, введите команду /start и авторизуйтесь."
        )
        return

    else:
        set_user_token(chat_id, token)

    keyboard = create_options_keyboard()

    user_notifications = get_user_notifications()
    if chat_id in user_notifications:
        try:
            await message.bot.delete_message(chat_id, user_notifications[chat_id])
        except Exception:
            logging.error(f"Не удалось удалить сообщение уведомления.")
        finally:
            remove_user_notification(chat_id)

    try:
        await message.delete()
    except Exception:
        logging.error(f"Не удалось удалить сообщение с токеном.")

    await message.answer(
        "✅ Токен успешно добавлен! Вы успешно авторизованы и можете использовать бота дальше.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "refresh_token")
async def refresh_token(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_notifications = get_user_notifications()

    if chat_id in user_notifications:
        try:
            await callback_query.bot.delete_message(
                chat_id, user_notifications[chat_id]
            )
        except Exception:
            logging.error(
                "Не удалось удалить сообщение уведомления при обновлении токена."
            )
        finally:
            remove_user_notification(chat_id)

    remove_user_token(chat_id)

    try:
        request_message = await callback_query.message.answer(
            "🔄 Чтобы обновить токен, пожалуйста, нажмите на кнопку ниже, чтобы авторизоваться заново."
        )

        keyboard = create_keyboard()
        token_message = await callback_query.message.answer(
            "👤 Авторизуйтесь, нажав на кнопку:", reply_markup=keyboard
        )

        set_user_notification(
            chat_id, (request_message.message_id, token_message.message_id)
        )
    except Exception:
        logging.error("Не удалось отправить сообщение при обновлении токена.")

from aiogram import types, Router, F
from aiogram.filters import Command
from tg_bot.global_state import (
    get_user_tokens,
    set_user_token,
    get_user_notifications,
    set_user_notification,
)

router = Router()


def create_keyboard():
    button = [
        [
            types.InlineKeyboardButton(
                text="Авторизоваться",
                url="https://school.mos.ru/?backUrl=https%3A%2F%2Fschool.mos.ru%2Fv2%2Ftoken%2Frefresh%3FroleId%3D1%26subsystem%3D4",
            ),
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=button)


@router.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = create_keyboard()
    notification = await message.answer(
        "Пожалуйста, нажмите на кнопку и войдите в аккаунт, затем скопируйте текст из куки и ответьте на это сообщение.",
        reply_markup=keyboard,
    )

    set_user_notification(message.from_user.id, notification.message_id)


@router.callback_query(F.data == "refresh_token")
async def refresh_token(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    get_user_tokens().pop(chat_id, None)

    await callback_query.message.answer(
        "Чтобы обновить токен, пожалуйста, введите новый токен ниже."
    )

    await callback_query.message.answer("Введите токен:")


@router.message(F.text)
async def process_token(message: types.Message):
    token = message.text
    chat_id = message.from_user.id

    set_user_token(chat_id, token)
    keyboard = create_options_keyboard()

    if chat_id in get_user_notifications():
        request_message_id, token_message_id = get_user_notifications()[chat_id]
        try:

            await message.bot.delete_message(chat_id, request_message_id)
            await message.bot.delete_message(chat_id, token_message_id)
            del get_user_notifications()[chat_id]
        except Exception as e:
            print(f"Failed to delete notification messages: {e}")

    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete token message: {e}")

    await message.answer(
        "Токен успешно обновлён! Теперь вы можете использовать бота.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


def create_options_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Расписание", callback_data="schedule"),
            types.InlineKeyboardButton(
                text="Домашние задания", callback_data="homework"
            ),
        ],
        [
            types.InlineKeyboardButton(text="Оценки", callback_data="marks"),
            types.InlineKeyboardButton(text="Профиль", callback_data="profile"),
        ],
        [
            types.InlineKeyboardButton(
                text="Оценки по дате", callback_data="marks_by_date"
            ),
            types.InlineKeyboardButton(
                text="Уведомления", callback_data="notifications"
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Обновить токен", callback_data="refresh_token"
            ),
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

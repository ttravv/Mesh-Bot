from aiogram import types, Router, F
from aiogram.filters import Command

router = Router()
user_tokens = {}
user_notifications = {}


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

    
    user_notifications[message.from_user.id] = notification.message_id


@router.callback_query(F.data == "refresh_token")
async def refresh_token(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_tokens.pop(chat_id, None)

    await callback_query.message.answer(
        "Чтобы обновить токен, пожалуйста, введите новый токен ниже."
    )

    await callback_query.message.answer("Введите токен:")


@router.message(F.text)
async def process_token(message: types.Message):
    token = message.text
    chat_id = message.from_user.id

    user_tokens[chat_id] = token
    keyboard = create_options_keyboard()


    if chat_id in user_notifications:
        request_message_id, token_message_id = user_notifications[chat_id]
        try:
           
            await message.bot.delete_message(chat_id, request_message_id)
            await message.bot.delete_message(chat_id, token_message_id)
            del user_notifications[chat_id]  
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
        ],
        [
            types.InlineKeyboardButton(
                text="Ответы на тест МЭШ", callback_data="test_answers"
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

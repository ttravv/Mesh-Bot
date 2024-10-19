from dnevniklib.student.student import Student
from aiogram import types, Router, F
from dnevniklib.errors.token import DnevnikTokenError
from tg_bot.global_state import (
    get_user_tokens,
    remove_user_token
)
import logging

router = Router()

@router.callback_query(F.data == "profile")
async def process_profile(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_tokens = get_user_tokens()  
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    try:
        student = Student(token)
        profile_info = (
            f"<b>👤 Имя:</b> {student.first_name or 'Не указано'}\n"
            f"<b>👥 Фамилия:</b> {student.last_name or 'Не указано'}\n"
            f"<b>🆔 Отчество:</b> {student.middle_name or 'Не указано'}\n"
            f"<b>🎂 Дата рождения:</b> {student.birthdate or 'Не указано'}\n"
            f"<b>📧 Email:</b> {student.email or 'Не указано'}\n"
            f"<b>🎓 Возраст:</b> {student.age or 'Не указано'}\n"
            f"<b>🚻 Пол:</b> {'Мужской' if student.sex == 'male' else 'Женский'}\n"
            f"<b>🏫 Класс:</b> {student.class_name or 'Не указано'}\n"
            f"<b>📚 ID студента:</b> {student.id or 'Не указано'}\n"
            f"<b>🏢 ID школы:</b> {student.school_id or 'Не указано'}\n"
            f"<b>🔑 Логин:</b> {student.login or 'Не указано'}"
        )
        await callback_query.message.answer(profile_info, parse_mode="HTML")
    except DnevnikTokenError:
        logging.error(f"Ошибка авторизации: токен недействителен.")
        remove_user_token(chat_id) 
        await callback_query.message.answer(
            "❌ Ошибка авторизации. Попробуйте обновить токен."
        )
    except Exception as e:
        logging.error(f"Произошла ошибка при получении профиля студента.")
        await callback_query.message.answer(
            f"❌ Произошла ошибка при получении профиля студента."
        )

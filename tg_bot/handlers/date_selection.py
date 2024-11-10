from aiogram import types, Router, F
from dnevniklib.calendar.calendar import Calendar
from datetime import datetime
from tg_bot.handlers.process_homework import fetch_homework
from tg_bot.handlers.process_marks import fetch_marks, fetch_marks_by_date
from tg_bot.handlers.process_schedule import fetch_schedule
from tg_bot.handlers.process_notifications import fetch_notifications
from tg_bot.global_state import get_user_tokens, get_user_state, set_user_state

router = Router()


@router.callback_query(F.data.startswith("date_"))
async def process_date_selection(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_tokens = get_user_tokens()
    token = user_tokens.get(chat_id)

    if not token:
        await callback_query.message.answer(
            "🚫 Вы не авторизованы. Пожалуйста, авторизуйтесь сначала."
        )
        return

    year, month, day = map(int, callback_query.data.split("_")[1:])
    selected_date = datetime(year, month, day)

    user_state = get_user_state()

    if user_state["action"] == "homework":
        await fetch_homework(callback_query, selected_date, token)

    if user_state["action"] == "marks_by_date":
        await fetch_marks_by_date(callback_query, selected_date, token)

    if user_state["action"] == "notifications":
        await fetch_notifications(callback_query, selected_date, token)

    if (chat_id in user_state) and ("start_date" in user_state[chat_id]):
        start_date = user_state["start_date"]
        end_date = selected_date
        user_state.pop("start_date")
        await fetch_marks(callback_query, chat_id, start_date, end_date)

    elif (
        chat_id in user_state
        and "start_date" not in user_state[chat_id]
        and user_state["action"] == "marks"
    ):
        user_state["start_date"] = selected_date
        set_user_state(chat_id, user_state)

        await callback_query.message.answer(
            "📅 Начальная дата выбрана. Теперь выберите конечную дату:"
        )

        calendar_instance = Calendar(
            chat_id,
            callback_query.message.message_id,
            process_date_selection,
            action="marks",
            user_state=user_state,
        )
        await calendar_instance.on_date(selected_date)

        msg_text, markup = await calendar_instance.setup_buttons()
        await callback_query.message.edit_text(msg_text, reply_markup=markup)

    else:
        calendar_instance = Calendar(
            chat_id,
            callback_query.message.message_id,
            process_date_selection,
            action=user_state["action"],
            user_state=user_state,
        )
        await calendar_instance.on_date(selected_date)

        if user_state["action"] == "schedule":
            await fetch_schedule(
                callback_query, calendar_instance.date1, selected_date, token
            )
        else:
            msg_text, markup = await calendar_instance.setup_buttons()
            await callback_query.message.edit_text(msg_text, reply_markup=markup)

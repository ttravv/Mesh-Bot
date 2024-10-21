from datetime import datetime
import calendar
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dateutil.relativedelta import relativedelta


class Calendar:
    def __init__(self, chat_id: int, message_id: int, callback, action: str, user_state: dict) -> None:
        self.chat_id = chat_id
        self.message_id = message_id
        self.callback = callback
        self.msg_text = "Выберите начальную дату"
        self.date = datetime.today()
        self.date1 = None
        self.action = action
        user_state['action'] = action

    async def setup_buttons(self):
        btns = [
            [
                InlineKeyboardButton(
                    text=self.date.strftime("%B %Y"), callback_data="ignore"
                )
            ]
        ]
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        btns.append(
            [InlineKeyboardButton(text=x, callback_data="ignore") for x in day_names]
        )
        cal = calendar.monthcalendar(self.date.year, self.date.month)
        today = datetime.today()

        for week in cal:
            week_btns = []
            for day in week:
                if day == 0:
                    week_btns.append(
                        InlineKeyboardButton(text=" ", callback_data="ignore")
                    )
                else:
                    this_date = datetime(
                        year=self.date.year, month=self.date.month, day=day
                    )
                    if self.date1 and this_date < self.date1:
                        week_btns.append(
                            InlineKeyboardButton(text=" ", callback_data="ignore")
                        )
                    else:
                        txt = str(day)
                        if (
                            day == today.day
                            and self.date.month == today.month
                            and self.date.year == today.year
                        ):
                            txt = f"[{txt}]"
                        week_btns.append(
                            InlineKeyboardButton(
                                text=txt,
                                callback_data=f"date_{self.date.year}_{self.date.month}_{day}",
                            )
                        )
            btns.append(week_btns)

        btns.append(
            [
                InlineKeyboardButton(text="◀️", callback_data="cal:left"),
                InlineKeyboardButton(text="❌", callback_data="cal:close"),
                InlineKeyboardButton(text="▶️", callback_data="cal:right"),
                InlineKeyboardButton(
                    text="Текущий месяц", callback_data="cal:current_month"
                ),
            ]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=btns)
        return self.msg_text, keyboard

    async def forward(self):
        self.date += relativedelta(months=1)
        return await self.setup_buttons()

    async def backward(self):
        self.date -= relativedelta(months=1)
        return await self.setup_buttons()

    async def close(self):
        return "Календарь закрыт", None

    async def on_date(self, date: datetime):
        if self.date1 is None:
            self.date1 = date
            self.msg_text = "Выберите конечную дату"
            return await self.setup_buttons()
        else:
            await self.callback(self.chat_id, self.date1, date)

    async def go_to_current_month(self):
        self.date = datetime.today()
        self.date1 = None
        return await self.setup_buttons()
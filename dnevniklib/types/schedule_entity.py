from pydantic import BaseModel

class ScheduleEntity(BaseModel):
    id: int
    date: str
    subject_list: list

    def __str__(self):
        res = f"<b>📅 Расписание на {self.date}</b>\n"

        time_slots = {}
        for item in self.subject_list:
            time_range = f"<b>{item['begin_time']}-{item['end_time']}</b>"
            if time_range not in time_slots:
                time_slots[time_range] = []
            time_slots[time_range].append(item)

        for time_range, subjects in time_slots.items():
            res += f"<b>\n🕒 {time_range}:\n</b>"
            for subject in subjects:
                res += f"<b>  • {subject['subject_name']} (Кабинет: {subject['room_number']})\n</b>"

        
        return res
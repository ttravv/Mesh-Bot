from pydantic import BaseModel

class ScheduleEntity(BaseModel):
    id: int
    date: str
    subject_list: list

    def __str__(self):
        res = f"📅 **Расписание на {self.date}**\n"
        res += "🟦" * 50 + "\n"

        time_slots = {}
        for item in self.subject_list:
            time_range = f"{item['begin_time']}-{item['end_time']}"
            if time_range not in time_slots:
                time_slots[time_range] = []
            time_slots[time_range].append(item)

        for time_range, subjects in time_slots.items():
            res += f"\n🕒 {time_range}:\n"
            for subject in subjects:
                res += f"  • {subject['subject_name']} (Кабинет: {subject['room_number']})\n"

        res += "🟦" * 50 + "\n"
        return res
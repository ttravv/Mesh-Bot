from aiogram.loggers import event
from dnevniklib import Student
from requests import get
from dnevniklib.types.event import Event
from datetime import datetime

class Notification:

    def __init__(self, student: Student) -> None:
        self.student = student

    def get_notification_by_date(self, selected_date: str):
        res = []

        response = get(
            f"https://school.mos.ru/api/family/mobile/v1/notifications/search?student_id={self.student.id}",
            headers={
                "Auth-Token": self.student.token,
                "Profile-Id": str(self.student.id),
                "x-mes-subsystem": "familymp",
            },
        )

        
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        for event in response.json():
           
            created_at = event["created_at"]
            if '.' in created_at:
                created_at = created_at.split('.')[0]  

           
            event_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").date()

           
            if event_date != selected_date:
                continue

       
            if event["event_type"] in {"create_homework", "update_homework"}:
                res.append(
                    Event(
                        date=created_at,
                        subject_name=event["subject_name"],
                        description=event.get("new_hw_description", "Нет описания"),
                    )
                )
            elif event["event_type"] in {"create_mark", "update_mark"}:
                res.append(
                    Event(
                        date=created_at,
                        subject_name=event["subject_name"],
                        description="Новая оценка: " + str(event.get("new_mark_value", "Нет оценки")),
                    )
                )
            elif event["event_type"] in {"create_mark_comment", "update_mark_comment"}:
                res.append(
                    Event(
                        date=created_at,
                        subject_name=event["subject_name"],
                        description="Обновлена оценка: " + str(event.get("new_mark_value", "Нет оценки")),
                    )
                )
            elif event["event_type"] == "delete_mark":
                res.append(
                    Event(
                        date=event.get("deleted_at", created_at),
                        subject_name=event["subject_name"],
                        description="Удалена оценка: " + str(event.get("old_mark_value", "Нет значения")),
                    )
                )

        return res

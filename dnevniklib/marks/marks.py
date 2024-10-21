from dnevniklib.student import Student
from requests import get
from dnevniklib.types import Mark


class Marks:
    def __init__(self, student: Student) -> None:
        self.student = student

    def get_marks_by_date(self, from_date, to_date):
        res = []
        response = get(
            f"https://school.mos.ru/api/family/web/v1/marks?student_id={self.student.id}&from={from_date}&to={to_date}",
            headers={"Auth-Token": self.student.token, "X-Mes-Subsystem": "familyweb"},
        )
        for mark in response.json()["payload"]:
            res.append(
                Mark(
                    id=mark["id"],
                    value=mark["value"],
                    comment=mark["comment"],
                    subject_name=mark["subject_name"],
                    subject_id=mark["subject_id"],
                    control_form_name=mark["control_form_name"],
                    weight=mark["weight"],
                    created_at=mark["created_at"],
                    is_exam=mark["is_exam"],
                )
            )
        return res


class MarksByDate:
    def __init__(self, student: Student) -> None:
        self.marks = Marks(student)

    def get_mark_for_date(self, date):
        marks = self.marks.get_marks_by_date(date, date)
        
        if not marks:
            return f"📅 <b>Оценок за {date} нет.</b>"
        
        res_str = f"📅 <b>Оценки за {date}:</b>\n" + "\n"
        
        for mark in marks:
            res_str += (
                f"   🌟 <b>{mark.subject_name}:</b> {mark.value} "
                f"<b>(💬 Комментарий: {mark.comment})\n</b>"
            )
     
        
        return res_str.strip()

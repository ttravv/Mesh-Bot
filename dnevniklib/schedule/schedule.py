from requests import get

from dnevniklib.types.schedule_entity import ScheduleEntity
from dnevniklib.types.subject import Subject

UNDEFINED_ID = -1


class Schedule:
    def __init__(self, student):
        self.student = student

    def get_schedule_by_date(self, date):
        response = get(
            f"https://school.mos.ru/api/family/web/v1/schedule?student_id={self.student.id}&date={date}",
            headers={
                "Auth-Token": self.student.token,
                "X-Mes-Subsystem": "familyweb"
            }
        )

        print(response.json())
        today = ScheduleEntity(
            id=UNDEFINED_ID,
            date=date,
            subject_list=[]
        )
        
        for activity in response.json().get('activities', []):
            if activity['type'] != 'BREAK':
                room_number = activity['room_number'] if activity['room_number'] is not None else "Не указано"
                end_time = activity.get('end_time', "Не указано")  
                
                today.subject_list.append({
                    'subject_name': activity['lesson']['subject_name'],
                    'begin_time': activity['begin_time'],
                    'end_time': end_time,
                    'room_number': room_number
                })

        return today

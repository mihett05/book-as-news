from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from core.database import create_db
from core.models import Preferences


class Analyzer:
    schedule: Dict[int, datetime]
    db: Session

    def __init__(self):
        self.db = create_db()
        self.schedule = dict()

    def generate_schedule(self):
        active_users: List[Preferences] = self.db.query(Preferences).filter(Preferences.is_active == True).all()
        for prefs in active_users:
            self.update_time_for_user(prefs)

    @staticmethod
    def get_next_time(prefs: Preferences) -> datetime:
        now = datetime.utcnow()
        last_time = datetime.fromtimestamp(prefs.last_sent_time)
        next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, seconds=prefs.start_time)
        delay = timedelta(seconds=prefs.delay)

        if prefs.last_sent_time == 0:
            if prefs.get_time(prefs.start_time) <= now.hour <= prefs.get_time(prefs.end_time):
                return now
            return next_day

        if prefs.get_time(prefs.start_time) <= now.hour <= prefs.get_time(prefs.end_time):
            if last_time.hour + prefs.get_time(prefs.delay) > prefs.get_time(prefs.end_time):
                return next_day
            return last_time + delay
        return next_day

    def update_time_for_user(self, prefs: Preferences):
        self.schedule[prefs.user_id] = self.get_next_time(prefs)

    def remove_user(self, prefs: Preferences):
        del self.schedule[prefs.user_id]
        prefs.is_active = False
        self.db.commit()

import re
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import Session
from aiogram.types import Message
from core.database import Base, create_db


class Preferences(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    fields = {
        "paragraphs_count": "pg_count",
        "delay": "delay",
        "start_time": "start_time",
        "end_time": "end_time",
        "timezone": "timezone"
    }

    paragraphs_count = Column(Integer, default=2)

    # в секундах всё ниже
    delay = Column(Integer, default=60 * 60 * 3)
    start_time = Column(Integer, default=60 * 60 * (12 - 5))  # utc
    end_time = Column(Integer, default=60 * 60 * (20 - 5))  # utc
    timezone = Column(Integer, default=60 * 60 * 5)
    last_sent_time = Column(Integer, default=0)
    last_sent_id = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    @classmethod
    def get_or_create(cls, db: Session, user_id: int) -> "Preferences":
        result = db.query(cls).filter(cls.user_id == user_id).first()
        if not result:
            result = Preferences(user_id=user_id)
            db.add(result)
            db.commit()
        return result

    @staticmethod
    def get_time(time: int) -> int:  # секунды в часы
        return time // (60 * 60)

    def get_message(self):
        return f"""
Настройки:
#️⃣Кол-во параграфов: {self.paragraphs_count}
🔂Интервал отправки: {self.get_time(self.delay)} ч.
Отправлять сообщения:
🕛С: {"%02d" % (self.get_time(self.start_time) + self.get_time(self.timezone))}:00
🕕До: {"%02d" % (self.get_time(self.end_time) + self.get_time(self.timezone))}:00
🌀Часовой пояс: {"+" if self.timezone >= 0 else "-"}{self.get_time(self.timezone)}
        """.strip()

    def validate_and_apply_field(self, key: str, value: int):
        error = None

        if key == "delay" and not (0 < value < (self.get_time(self.end_time) - self.get_time(self.start_time))):
            error = "Интервал больше период рабочего времени"
        elif key == "paragraphs_count" and not (1 <= value <= 10):
            error = "Разрешено от 1 до 10 абзацев"
        elif key == "start_time":
            if value > 23 or value < 0:
                error = "Невалидное начальное время"
            elif value > (self.get_time(self.end_time) + self.get_time(self.timezone)):
                error = "Начальное время позже конечного"
        elif key == "end_time":
            if value > 23 or value < 0:
                error = "Невалидное конечное время"
            elif value < (self.get_time(self.start_time) + self.get_time(self.timezone)):
                error = "Конечное время раньше начального"
        elif key == "timezone" and not (2 <= value <= 12):
            error = "Невалидный часовой пояс (от 2 до 12)"

        if error is not None:
            return error

        if key == "paragraphs_count":
            self.paragraphs_count = value
        elif key == "delay":
            setattr(self, key, value * 60 * 60)
        elif key == "timezone":
            diff = value * 60 * 60 - self.timezone
            setattr(self, key, value * 60 * 60)
            self.start_time -= diff
            self.end_time -= diff
        elif key in ["start_time", "end_time"]:
            setattr(self, key, value * 60 * 60 - self.timezone)


def get_prefs(msg: Message) -> (Session, Preferences):
    db = create_db()
    prefs = Preferences.get_or_create(db, msg.from_user.id)
    return db, prefs

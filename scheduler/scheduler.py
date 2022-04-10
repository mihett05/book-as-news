import asyncio
from datetime import datetime
from typing import List
from aiogram import Bot
from core.models import Preferences, Paragraph
from .analyzer import Analyzer


class Scheduler:
    def __init__(self, bot: Bot):
        self.analyzer = Analyzer()
        self.analyzer.generate_schedule()
        self.bot = bot

    def get_next_time_for_user(self, user_id: int) -> datetime:
        return self.analyzer.schedule[user_id]

    def add_new_user(self, prefs: Preferences):
        self.analyzer.update_time_for_user(prefs)

    def update_preferences(self, prefs: Preferences):
        self.analyzer.update_time_for_user(prefs)

    def get_next_paragraph(self, prefs: Preferences) -> List[Paragraph]:
        return self.analyzer.db.query(Paragraph)\
            .filter(Paragraph.id >= prefs.last_sent_id + 1)\
            .filter(Paragraph.id <= prefs.last_sent_id + prefs.paragraphs_count)\
            .all()

    async def schedule(self):
        while True:
            next_user_id = min(self.analyzer.schedule, key=lambda x: self.analyzer.schedule[x])
            prefs: Preferences = self.analyzer.db.query(Preferences).filter(Preferences.user_id == next_user_id).first()
            time_to_wait = (
               self.get_next_time_for_user(next_user_id).replace(microsecond=0)
               -
               datetime.utcnow().replace(microsecond=0)
            )

            paragraphs = self.get_next_paragraph(prefs)
            if not paragraphs:
                await self.bot.send_message(prefs.user_id, "Конец книги")
                self.analyzer.remove_user(prefs)
                continue

            if time_to_wait.total_seconds() > 0:
                await asyncio.sleep(time_to_wait.seconds)
            for paragraph in paragraphs:
                path = "".join([
                    paragraph.volume,
                    ". " if paragraph.volume else "",
                    paragraph.part,
                    ". " if paragraph.part else "",
                    paragraph.chapter,
                    "\n\n"
                ])
                await self.bot.send_message(next_user_id, path + paragraph.content + "\n\n" + paragraph.notes)
            prefs.last_sent_time = int(datetime.utcnow().timestamp())
            prefs.last_sent_id = paragraphs[-1].id
            self.analyzer.db.commit()
            self.update_preferences(prefs)

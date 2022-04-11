import asyncio
from datetime import datetime
from typing import List, Union
from aiogram import Bot
from core.models import Preferences, Paragraph
from .analyzer import Analyzer


class Scheduler:
    _instance = None
    bot: Bot

    def __init__(self):
        self.analyzer = Analyzer()
        self.analyzer.generate_schedule()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Scheduler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_current_scheduler(cls) -> "Scheduler":
        return cls._instance

    def set_bot(self, bot: Bot):
        self.bot = bot

    def get_next_time_for_user(self, user_id: int) -> datetime:
        return self.analyzer.schedule[user_id]

    def add_new_user(self, prefs: Preferences):
        self.analyzer.update_time_for_user(prefs)

    async def remove_user(self, prefs: Preferences):
        await self.bot.send_message(prefs.user_id, "Конец книги", parse_mode="Markdown")
        self.analyzer.remove_user(prefs)

    def update_preferences(self, prefs: Preferences):
        self.analyzer.update_time_for_user(prefs)

    def get_next_paragraphs(self, prefs: Preferences, count: int = None) -> List[Paragraph]:
        count = count or prefs.paragraphs_count
        return self.analyzer.db.query(Paragraph)\
            .filter(Paragraph.id >= prefs.last_sent_id + 1)\
            .filter(Paragraph.id <= prefs.last_sent_id + count)\
            .all()

    async def send_next_paragraphs(self, prefs: Preferences, paragraphs: List[Paragraph]):
        for paragraph in paragraphs:
            path = "".join([
                paragraph.volume,
                ". " if paragraph.volume else "",
                paragraph.part,
                ". " if paragraph.part else "",
                paragraph.chapter,
                "\n\n"
            ])
            await self.bot.send_message(
                prefs.user_id,
                path + paragraph.content + "\n\n" + paragraph.notes,
                parse_mode="Markdown"
            )
        prefs.last_sent_time = int(datetime.utcnow().timestamp())
        prefs.last_sent_id = paragraphs[-1].id
        self.analyzer.db.commit()
        self.update_preferences(prefs)

    async def schedule(self):
        while True:
            next_user_id = min(self.analyzer.schedule, key=lambda x: self.analyzer.schedule[x])
            prefs: Preferences = self.analyzer.db.query(Preferences).filter(Preferences.user_id == next_user_id).first()
            time_to_wait = (
               self.get_next_time_for_user(next_user_id).replace(microsecond=0)
               -
               datetime.utcnow().replace(microsecond=0)
            )

            paragraphs = self.get_next_paragraphs(prefs)
            if not paragraphs:
                await self.remove_user(prefs)
                continue

            if time_to_wait.total_seconds() > 0:
                await asyncio.sleep(time_to_wait.seconds)

            if prefs.last_sent_id != paragraphs[0].id - 1:
                paragraphs = self.get_next_paragraphs(prefs)
                if not paragraphs:
                    await self.remove_user(prefs)
                    continue

            await self.send_next_paragraphs(prefs, paragraphs)

from aiogram.types import Message
from sqlalchemy.orm import Session
from core.models import Preferences
from core.database import create_db
from core.keyboard import settings_keyboard
from scheduler import Scheduler


def get_prefs(msg: Message) -> (Session, Preferences):
    db = create_db()
    prefs = Preferences.get_or_create(db, msg.from_user.id)
    return db, prefs


async def send_settings(message: Message):
    db, prefs = get_prefs(message)
    if prefs.settings_message_id:
        await message.bot.delete_message(prefs.user_id, prefs.settings_message_id)
    msg = await message.answer(prefs.get_message(), reply_markup=settings_keyboard)
    prefs.settings_message_id = msg.message_id
    db.commit()


async def update_settings(message: Message, key: str, value: int) -> str:
    scheduler = Scheduler.get_current_scheduler()
    db, prefs = get_prefs(message)
    error = prefs.validate_and_apply_field(key, value)
    if not error:
        db.commit()
        scheduler.update_preferences(prefs)
    return error

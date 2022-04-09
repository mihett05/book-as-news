import os
import re
from aiogram import Bot, Dispatcher, executor, types, filters
from sqlalchemy.orm import Session

from core.database import Base, engine, create_db
from core.models import Paragraph, Preferences
from core.models.preferences import get_prefs, pref_handler


bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher(bot)


async def on_startup(dispatcher: Dispatcher, url=None, cert=None):
    Base.metadata.create_all(bind=engine)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("abcd123 *test*", parse_mode="Markdown")


@dp.message_handler(commands=["settings"])
async def settings_handler(message: types.Message):
    user_id = message.from_user.id
    db, prefs = get_prefs(message)
    await message.answer(prefs.get_message())


def create_pref_handler(key):
    @dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[rf"set_{Preferences.fields[key]} ([0-9]+)"]))
    @pref_handler
    async def set_field_handler(message: types.Message, arg: int, db: Session, prefs: Preferences):
        error = prefs.validate_and_apply_field(key, arg)
        if error:
            await message.answer(error)
            return False
        return True


for field in Preferences.fields:
    create_pref_handler(field)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

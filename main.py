import os
import re
import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters, middlewares


from core.database import Base, engine
from core.models import Preferences
from core.models.preferences import get_prefs
from scheduler import Scheduler


bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()
scheduler: Scheduler


class PrefsMiddleware(middlewares.BaseMiddleware):
    async def on_process_message(self, message: types.Message, data):
        db, prefs = get_prefs(message)
        if prefs.last_sent_time == 0:
            scheduler.add_new_user(prefs)


async def on_startup(dispatcher: Dispatcher, url=None, cert=None):
    global scheduler
    Base.metadata.create_all(bind=engine)
    scheduler = Scheduler(bot)
    loop.create_task(scheduler.schedule())


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("abcd123 *test*", parse_mode="Markdown")


@dp.message_handler(commands=["settings"])
async def settings_handler(message: types.Message):
    db, prefs = get_prefs(message)
    await message.answer(prefs.get_message())


@dp.message_handler(commands=["next_time"])
async def next_time(message: types.Message):
    user_id = message.from_user.id
    await message.answer(scheduler.get_next_time_for_user(user_id).isoformat())


def create_pref_handler(key):
    @dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[rf"set_{Preferences.fields[key]} ([0-9]+)"]))
    async def set_field_handler(message: types.Message, regexp_command: re.Match):
        arg = int(regexp_command.group(1))
        db, prefs = get_prefs(message)
        error = prefs.validate_and_apply_field(key, arg)
        if error:
            await message.answer(error)
        else:
            db.commit()
            await message.answer(prefs.get_message())
            scheduler.update_preferences(prefs)


for field in Preferences.fields:
    create_pref_handler(field)


if __name__ == '__main__':
    dp.setup_middleware(PrefsMiddleware())
    executor.start_polling(dp, loop=loop, skip_updates=True, on_startup=on_startup)

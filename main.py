import os
import re
import asyncio
from aiogram import Bot, Dispatcher, executor, types, middlewares
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.utils import get_prefs
from core.database import Base, engine
from scheduler import Scheduler

from core.handlers import init_commands, init_callbacks


bot = Bot(token=os.getenv("TG_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()
scheduler: Scheduler


class PrefsMiddleware(middlewares.BaseMiddleware):
    async def on_process_message(self, message: types.Message, data):
        await message.delete()
        db, prefs = get_prefs(message)
        if prefs.last_sent_time == 0:
            scheduler.add_new_user(prefs)


async def on_startup(dispatcher: Dispatcher, url=None, cert=None):
    global scheduler
    Base.metadata.create_all(bind=engine)
    scheduler = Scheduler()
    scheduler.set_bot(bot)
    loop.create_task(scheduler.schedule())

    init_commands(dispatcher)
    init_callbacks(dispatcher)


if __name__ == '__main__':
    dp.setup_middleware(PrefsMiddleware())
    executor.start_polling(dp, loop=loop, skip_updates=True, on_startup=on_startup)

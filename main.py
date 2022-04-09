import os
from aiogram import Bot, Dispatcher, executor, types

from core.database import Base, engine
from core.models import *


bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher(bot)


async def on_startup(dispatcher: Dispatcher, url=None, cert=None):
    Base.metadata.create_all(bind=engine)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("abcd123 *test*", parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

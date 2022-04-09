import os
from aiogram import Bot, Dispatcher, executor, types


bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("abcd123 *test*", parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

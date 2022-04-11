import re
from aiogram import Dispatcher, types, filters


from core.models import Preferences
from core.utils import send_settings, update_settings
from core.keyboard import keyboard
from scheduler import Scheduler


async def start_handler(message: types.Message):
    await message.answer("Нажми на кнопки снизу", parse_mode="Markdown", reply_markup=keyboard)
    await send_settings(message)


async def next_time(message: types.Message):
    user_id = message.from_user.id
    scheduler = Scheduler.get_current_scheduler()
    await message.answer(scheduler.get_next_time_for_user(user_id).isoformat())


def create_pref_handler(dp: Dispatcher, key: str):
    async def set_field_handler(message: types.Message, regexp_command: re.Match):
        arg = int(regexp_command.group(1))
        error = await update_settings(message, key, arg)
        if error:
            await message.answer(error)
        else:
            await send_settings(message)
    dp.register_message_handler(
        set_field_handler,
        filters.RegexpCommandsFilter(regexp_commands=[rf"set_{Preferences.fields[key]} ([0-9]+)"])
    )


def init_commands(dp: Dispatcher):
    dp.register_message_handler(start_handler, filters.CommandStart())
    dp.register_message_handler(send_settings, lambda msg: "настройки" in msg.text.lower())
    dp.register_message_handler(send_settings, commands=["settings"])
    dp.register_message_handler(next_time, commands=["next_time"])

    for field in Preferences.fields:
        create_pref_handler(dp, field)

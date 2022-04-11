import re
from datetime import timedelta
from aiogram import Dispatcher, types, filters


from core.models import Preferences
from core.utils import get_prefs, send_settings, update_settings
from core.keyboard import keyboard
from scheduler import Scheduler


async def start_handler(message: types.Message):
    await message.answer("Нажми на кнопки снизу", parse_mode="Markdown", reply_markup=keyboard)


async def next_time(message: types.Message):
    db, prefs = get_prefs(message)
    scheduler = Scheduler.get_current_scheduler()
    utc_next = scheduler.get_next_time_for_user(prefs.user_id)
    await message.answer((utc_next + timedelta(hours=prefs.get_time(prefs.timezone))).isoformat())


async def get_more_paragraph(message: types.Message):
    db, prefs = get_prefs(message)
    scheduler = Scheduler.get_current_scheduler()
    paragraphs = scheduler.get_next_paragraphs(prefs, count=1)
    if not paragraphs:
        await scheduler.remove_user(prefs)
    else:
        await scheduler.send_next_paragraphs(prefs, paragraphs)
    db.commit()


async def clear(message: types.Message):
    db, prefs = get_prefs(message)
    scheduler = Scheduler.get_current_scheduler()
    prefs.last_sent_id = 0
    db.commit()
    scheduler.add_new_user(prefs)
    await message.answer("Прочтение начато с начала")


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
    dp.register_message_handler(send_settings, lambda msg: "настройки" in msg.text.strip().lower())
    dp.register_message_handler(send_settings, commands=["settings"])

    dp.register_message_handler(next_time, lambda msg: "следующее время отправки" in msg.text.strip().lower())
    dp.register_message_handler(next_time, commands=["next_time"])

    dp.register_message_handler(get_more_paragraph, lambda msg: "отправить ещё абзац" in msg.text.strip().lower())
    dp.register_message_handler(get_more_paragraph, commands=["next_pg"])

    dp.register_message_handler(clear, commands=["clear"])

    for field in Preferences.fields:
        create_pref_handler(dp, field)

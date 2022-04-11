from functools import reduce
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from core.models.preferences import Preferences

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
keyboard.row(KeyboardButton("⚙️ Настройки"))
keyboard.row(KeyboardButton("⏭️ Отправить ещё абзац"), KeyboardButton("⏱️ Следующее время отправки"))

settings_keyboard = InlineKeyboardMarkup(row_width=3)
set_pg_count_button = InlineKeyboardButton("Кол-во абзацев", callback_data="paragraphs_count")
set_delay_button = InlineKeyboardButton("Интервал", callback_data="delay")
set_timezone_button = InlineKeyboardButton("Часовой пояс", callback_data="timezone")
set_start_button = InlineKeyboardButton("Начало", callback_data="start_time")
set_end_button = InlineKeyboardButton("Конец", callback_data="end_time")

settings_keyboard.row(set_pg_count_button, set_delay_button, set_timezone_button)
settings_keyboard.row(set_start_button, set_end_button)
settings_buttons = reduce(lambda a, b: a + b, settings_keyboard.inline_keyboard, [])

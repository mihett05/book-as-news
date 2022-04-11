from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from core.utils import send_settings, update_settings
from core.keyboard import settings_buttons


class SettingsForm(StatesGroup):
    paragraphs_count = State()
    delay = State()
    start_time = State()
    end_time = State()
    timezone = State()


def create_inline_handler(dp: Dispatcher, inline: types.InlineKeyboardButton):
    async def inline_handler(message: types.Message):
        await getattr(SettingsForm, inline.callback_data).set()
        await message.answer("Введите значение")
    dp.register_callback_query_handler(inline_handler, text=inline.callback_data)


def create_answer_handler(dp: Dispatcher, inline: types.InlineKeyboardButton):
    async def state_handler(message: types.Message, state: FSMContext):
        value = int(message.text.strip())
        error = await update_settings(message, inline.callback_data, value)
        if error:
            await message.answer(error + "\n" + "Введите корректное значение")
        else:
            await state.finish()
            await send_settings(message)
    dp.register_message_handler(state_handler, state=getattr(SettingsForm, inline.callback_data))


def init_callbacks(dp: Dispatcher):
    for button in settings_buttons:
        create_inline_handler(dp, button)
        create_answer_handler(dp, button)

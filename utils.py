import json

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def save_users(new_users: dict):
    with open('users.json', 'w', encoding='utf-8') as f2:
        f2.write(json.dumps(new_users, ensure_ascii=False, indent=4))


def ok_button_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='ОК', callback_data='del'))
    return keyboard.as_markup()


async def delete_message(data):
    message: types.Message = data.message if isinstance(data, types.CallbackQuery) else data
    try:
        await message.delete()
    except Exception:
        pass

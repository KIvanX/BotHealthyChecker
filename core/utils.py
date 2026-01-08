import asyncio
import json
import os

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telethon import TelegramClient


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

async def restart_tg_client(tg_client):
    await tg_client.disconnect()
    await asyncio.sleep(5)
    tg_client = TelegramClient(session='tg_session',
                               api_id=int(os.environ['TELETHON_API_ID']),
                               api_hash=os.environ['TELETHON_API_HASH'],
                               device_model="iPhone 13 Pro Max",
                               system_version='4.16.30-vxCUSTOM',
                               app_version="8.4",
                               lang_code="en",
                               system_lang_code="en-US")
    return tg_client


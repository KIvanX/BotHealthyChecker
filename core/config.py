import json
import logging
import sys
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from telethon import TelegramClient
from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    bot_username = State()
    bot_period = State()


dotenv.load_dotenv()
bot = Bot(token=os.environ['TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
tg_client = TelegramClient(session='tg_session',
                           api_id=int(os.environ['TELETHON_API_ID']),
                           api_hash=os.environ['TELETHON_API_HASH'],
                           device_model="iPhone 13 Pro Max",
                           system_version='4.16.30-vxCUSTOM',
                           app_version="8.4",
                           lang_code="en",
                           system_lang_code="en-US")

with open('users.json', 'r', encoding='utf-8') as f1:
    users = json.load(f1)


logging.root.handlers.clear()
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s\n" + '_' * 100,
    handlers=[
        logging.FileHandler("logs.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


import asyncio
import logging

from config import users, bot
from tg_client import ping_bot


async def checker():
    while True:
        try:
            await asyncio.sleep(60)
            for user_id in users:
                for user_bot in users[user_id]['bots']:
                    if user_bot['status'] != 'stop':
                        continue

                    answer = await ping_bot(user_bot['username'])
                    if answer['status'] != 'ok':
                        await bot.send_message(chat_id=user_id,
                                               text=f'❗️ Бот <a href="https://t.me/{user_bot["username"]}">'
                                                    f'{user_bot['name']}</a> перестал отвечать на команду /start')
                    await asyncio.sleep(1)
        except Exception as e:
            logging.error(e, exc_info=True)
            await asyncio.sleep(60)

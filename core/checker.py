import asyncio
import logging

from core.config import users, bot
from core.tg_client import ping_bot


async def checker():
    await asyncio.sleep(10)
    while True:
        for user_id in users:
            for user_bot in users[user_id].get('bots', []):
                try:
                    if user_bot['status'] == 'stop':
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

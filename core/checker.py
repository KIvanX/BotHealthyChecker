import asyncio
import logging
import random
import time

from core.config import users, bot, tg_client
from core.tg_client import ping_bot
from core.utils import restart_tg_client, save_users


async def checker():
    await asyncio.sleep(10)
    while True:
        for user_id in users:
            for user_bot in users[user_id].get('bots', []):
                try:
                    if user_bot['status'] == 'stop' or user_bot.get('last_check', 0) > time.time() - user_bot['period'] * 60:
                        continue

                    answer = await ping_bot(user_bot['username'])
                    if answer['status'] != 'ok':
                        logging.error(f'Error bot ping status: {answer}')
                        if answer.get('error', '').startswith('A wait of'):
                            await restart_tg_client(tg_client)
                            continue

                        await bot.send_message(chat_id=user_id,
                                               text=f'❗️ Бот <a href="https://t.me/{user_bot["username"]}">'
                                                    f'{user_bot['name']}</a> перестал отвечать на команду /start')

                    user_bot['last_check'] = time.time()
                    save_users(users)
                    await asyncio.sleep(1 + random.random() * 2)
                except Exception as e:
                    logging.error(e, exc_info=True)

        await asyncio.sleep(3)

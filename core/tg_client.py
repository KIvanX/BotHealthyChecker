import asyncio
import logging
import time

from telethon import events

from core.config import tg_client


async def get_bot(username: str):
    try:
        print(username)
        chat = await tg_client.get_entity(username)
        print(chat)
        return chat
    except Exception as e:
        logging.error(e, exc_info=True)
        return None


async def ping_bot(username: str, timeout=30):
    bot = await get_bot(username)
    if not bot:
        return {
            "status": "error",
            "response_time": None,
            "error": 'Bot not found',
        }

    response_event = asyncio.Event()
    response_message = {}

    @tg_client.on(events.NewMessage(from_users=bot.id))
    async def handler(event):
        await event.mark_read()
        response_message["text"] = event.message.text
        response_event.set()

    t0 = time.time()
    try:
        await tg_client.send_message(bot, "/start")
    except Exception as e:
        return {
            "status": "error",
            "response_time": None,
            "error": str(e)
        }

    try:
        await asyncio.wait_for(response_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        tg_client.remove_event_handler(handler)
        return {
            "status": "timeout",
            "response_time": None
        }

    tg_client.remove_event_handler(handler)

    return {
        "status": "ok",
        "response_time": round(time.time() - t0, 2),
        "response_text": response_message.get("text")
    }

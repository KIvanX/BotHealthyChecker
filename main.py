import asyncio
import logging
import os
from datetime import datetime

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.checker import checker
from core.config import bot, dp, tg_client, AddBotStates, users
from core.tg_client import get_bot, ping_bot
from core.utils import ok_button_keyboard, save_users, delete_message


@dp.startup()
async def on_start():
    await bot.set_my_commands([types.BotCommand(command='start', description='Старт')])
    asyncio.create_task(checker())


@dp.shutdown()
async def on_shutdown():
    await tg_client.disconnect()
    await bot.session.close()


@dp.message(Command('logs'))
async def get_logs(message: types.Message):
    if str(message.chat.id) in os.environ.get('ADMINS', '').split(','):
        await delete_message(message)
        await bot.send_document(message.chat.id, FSInputFile('logs.log'), reply_markup=ok_button_keyboard())

        with open('logs.log', 'w') as file:
            file.write(str(datetime.now()) + '\n')


@dp.callback_query(F.data == 'start')
@dp.message(Command('start'))
async def start(data):
    message: types.Message = data.message if isinstance(data, types.CallbackQuery) else data
    keyboard = InlineKeyboardBuilder()
    if str(message.chat.id) not in users:
        users[str(message.chat.id)] = {'username': message.chat.username, 'bots': []}
        save_users(users)

    for user_bot in users[str(message.chat.id)]['bots']:
        keyboard.add(types.InlineKeyboardButton(text=user_bot["name"], callback_data=f'bot_{user_bot["username"]}'))

    keyboard.adjust(2)
    keyboard.row(types.InlineKeyboardButton(text='➕ Добавить бота', callback_data='add_bot'))

    send_message = message.edit_text if isinstance(data, types.CallbackQuery) else message.answer
    await send_message('🩺 <b>Привет!</b> Я помогу тебе следить за состоянием любого <i>telegram</i> бота.\n\n'
                       'Добавь в список ботов, за работой которых нужно следить. '
                       'В случае если бот перестанет отвечать, я отправлю тебе уведомление.',
                       reply_markup=keyboard.as_markup())


@dp.callback_query(F.data == 'add_bot')
async def add_bot(call: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='🏠 Назад', callback_data='start'))

    await state.set_state(AddBotStates.bot_username)
    await call.message.edit_text('✏️ Введи <code>username</code> своего бота, я сообщу если он перестанет работать.',
                                 reply_markup=keyboard.as_markup())


@dp.message(F.text[0] != '/', AddBotStates.bot_username)
async def save_new_bot(message: types.Message):
    username = message.text.replace('@', '').replace('https://t.me/', '')
    bot_info = await get_bot(username)

    if bot_info is None:
        await message.delete()
        await message.answer(f'🤷 Бот <b>{username}</b> не найден, '
                             f'проверь <code>username</code> и попробуй снова',
                             reply_markup=ok_button_keyboard())
        return 0
    elif not bot_info:
        await message.delete()
        await message.answer(f'🚫 Этот username не бота',
                             reply_markup=ok_button_keyboard())
        return 0

    answer = await ping_bot(username, timeout=3)
    if answer['status'] != 'ok':
        await message.delete()
        await message.answer(f'⛔️ Этот бот не отвечает',
                             reply_markup=ok_button_keyboard())
        return 0

    users[str(message.chat.id)]['bots'].append({'id': bot_info.id, 'username': username,
                                                'name': bot_info.first_name, 'status': 'start'})
    save_users(users)

    await start(message)


@dp.callback_query(F.data.startswith('bot_'))
async def bot_menu(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('bot_'):
        user_bot = next((b for b in users[str(call.message.chat.id)]['bots'] if b['username'] == call.data[4:]), None)
    else:
        state_data = await state.get_data()
        user_bot = next((b for i, b in enumerate(users[str(call.message.chat.id)]['bots'])
                         if b['username'] == state_data['username']), None)

    status_text = '💤 Остановить отслеживание' if user_bot['status'] == 'start' else '🆙 Запустить отслеживание'
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text=status_text, callback_data='switch_status_bot'))
    keyboard.row(types.InlineKeyboardButton(text='🗑 Удалить', callback_data='delete_bot_confirm'))
    keyboard.row(types.InlineKeyboardButton(text='🏠 Назад', callback_data='start'))


    answer = await ping_bot(user_bot['username'], timeout=3)
    text = (f'🤖 Бот <b>{user_bot['name']}</b>\n\n'
            f'Чат: @{user_bot["username"]}\n'
            f'Отслеживание работы: <b>{"🆙 Запущено" if user_bot["status"] == "start" else "💤 Остановлено"}</b>\n'
            f'Состояние: <b>{"🟢 Работает" if answer["status"] == 'ok' else "🔴 Не отвечает"}</b>\n')

    if answer['status'] == 'ok':
        response_text = answer["response_text"][:50] + '...' if len(answer["response_text"]) > 50 else answer["response_text"]
        text += (f'Ожидание ответа: <b>{answer["response_time"]}</b> сек\n\n'
                 f'Ответ на команду <code>start</code>:\n{response_text}\n')

    await state.update_data(username=user_bot['username'])
    await call.message.edit_text(text, reply_markup=keyboard.as_markup())


@dp.callback_query(F.data == 'delete_bot_confirm')
async def delete_bot_confirm(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='✅ Подтвердить', callback_data='delete_bot'))
    keyboard.row(types.InlineKeyboardButton(text='🏠 Назад', callback_data='bot_' + state_data['username']))

    await call.message.edit_text(f'❕ Подтверди удаление бота @{state_data['username']} из отслеживаемых',
                                 reply_markup=keyboard.as_markup())


@dp.callback_query(F.data == 'delete_bot')
async def delete_bot(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    bot_index = next((i for i, b in enumerate(users[str(call.message.chat.id)]['bots'])
                      if b['username'] == state_data['username']), None)
    users[str(call.message.chat.id)]['bots'].pop(bot_index)
    save_users(users)

    await call.answer('🗑 Бот удален')
    await start(call)


@dp.callback_query(F.data == 'switch_status_bot')
async def switch_status_bot(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    user_bot = next((b for i, b in enumerate(users[str(call.message.chat.id)]['bots'])
                      if b['username'] == state_data['username']), None)
    user_bot['status'] = 'stop' if user_bot['status'] == 'start' else 'start'
    save_users(users)

    await call.answer('✅ Готово')
    await bot_menu(call, state)


async def main():
    dp.message.register(start, Command('start'))
    dp.callback_query.register(delete_message, F.data == 'del')

    await tg_client.start()
    logging.warning('Bot is running...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

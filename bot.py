import asyncio
import os

import schedule
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from config import Config
from handlers.bazaraki_handler import check_ads, clear_previous_ads
import configparser
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
c = Config()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)

SUBSCRIBERS = set()
is_settings_mode = False
config_callback = CallbackData('config', 'field')

buttons = InlineKeyboardMarkup(row_width=2)
buttons.add(
    InlineKeyboardButton('Min price', callback_data=config_callback.new(field='min_price')),
    InlineKeyboardButton('Max price', callback_data=config_callback.new(field='max_price')),
    InlineKeyboardButton('City', callback_data=config_callback.new(field='city')),
    InlineKeyboardButton('Min rooms', callback_data=config_callback.new(field='min_rooms')),
    InlineKeyboardButton('Max rooms', callback_data=config_callback.new(field='max_rooms')),
    InlineKeyboardButton('Count photo', callback_data=config_callback.new(field='count_photo'))
)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    SUBSCRIBERS.add(message.chat.id)

    await message.reply("Hi, I'm the apartment bot. I will send you new apartment ads every 5 minutes.")
    clear_previous_ads()
    asyncio.create_task(monitor_ads())


@dp.message_handler(commands=['stop'])
async def stop_command(message: types.Message):
    SUBSCRIBERS.discard(message.chat.id)
    await message.reply("Goodbye! You will no longer receive apartment ads from me.")


@dp.message_handler(commands=['settings'])
async def settings_mode_on(message: types.Message):
    await bot.send_message(message.chat.id, 'Выберите поле для изменения:', reply_markup=buttons)


@dp.callback_query_handler(config_callback.filter())
async def process_config_callback(query: CallbackQuery, callback_data: dict):
    global current_field
    current_field = callback_data['field']
    await bot.send_message(query.from_user.id, f'Введите новое значение для {current_field}:')


@dp.message_handler()
async def process_message(message: types.Message):
    global current_field
    new_value = message.text
    update_config(current_field, new_value)
    await bot.send_message(message.chat.id, f'Значение {current_field} изменено на {new_value}.')
    current_field = ''


async def monitor_ads():
    schedule.every(c.clearing).days.do(clear_previous_ads)

    while True:
        schedule.run_pending()
        await check_ads(bot)
        await asyncio.sleep(c.interval)


def update_config(field: str, value: str):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config['requirements'][field] = value
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    executor.start_polling(dp)
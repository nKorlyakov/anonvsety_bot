# Main file for start bot
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from sqlalchemy import  create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import config
import strings_const
import user_worker
from logger import CustomLogger
import utils
import admin


bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp_tech_pause = Dispatcher(bot, storage=MemoryStorage())

engine = create_engine('sqlite:///../database.db')
session = Session(engine)

logger = CustomLogger()


@dp.message_handler(commands=['help'], state='*')
async def get_help_menu(message: types.Message):
    await message.answer(strings_const.HELP_TEXT)


@dp.message_handler(commands=['menu'], state='*')
async def get_menu(message: types.Message):
    await start(message, is_admin_mode=False)


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, is_admin_mode=True):
    utils.register_user(session, logger, message.from_user)
    if utils.is_admin_mode(session, message.from_user.id) and is_admin_mode:
        await admin_menu(message)
    else:
        search_keyboard = KeyboardButton(strings_const.SEARCH_TEXT)
        rating_keyboard = KeyboardButton(strings_const.RATING_TEXT)
        profile_keyboard = KeyboardButton(strings_const.PROFILE_TEXT)
        info_keyboard = KeyboardButton(strings_const.INFO_TEXT)

        keyboards_menu = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboards_menu.add(search_keyboard).add(rating_keyboard).add(profile_keyboard).add(info_keyboard)

        await message.answer(strings_const.WELCOME_TEXT, reply_markup=keyboards_menu)


async def admin_menu(message: types.Message):
    distribution_keyboard = InlineKeyboardButton(strings_const.DISTRIBUTION_TEXT, callback_data='distribution')

    keyboards_admin_menu = InlineKeyboardMarkup()
    keyboards_admin_menu.add(distribution_keyboard)

    await message.answer(strings_const.ADMIN_TEMPLATE.substitute(), reply_markup=keyboards_admin_menu)


@dp.callback_query_handler(lambda callback: callback.data in config.ALL_ADMIN_COMMAND, state='*')
async def admin_commands(callback_query: types.CallbackQuery):
    await admin.admin_command_routing(callback_query, bot, dp)


@dp.message_handler(lambda message: message.text in (strings_const.SEARCH_TEXT, '/search'), state='*')
async def search_companion(message: types.Message):
    await user_worker.search_companion(message)


@dp.message_handler(lambda message: message.text in (strings_const.RATING_TEXT, '/rating'), state='*')
async def get_rating(message: types.Message):
    await user_worker.get_rating(message)


@dp.message_handler(lambda message: message.text in (strings_const.PROFILE_TEXT, '/profile'), state='*')
async def get_profile(message: types.Message):
    await user_worker.get_profile(message)


@dp.message_handler(lambda message: message.text in (strings_const.INFO_TEXT, '/info'), state='*')
async def get_information_menu(message: types.Message):
    send_bug_report_keyboard = KeyboardButton(strings_const.SEND_BUG_REPORT_TEXT)
    help_keyboard = KeyboardButton(strings_const.HELP_LINK_TEXT)
    support_keyboard = KeyboardButton(strings_const.SUPPORT_TEXT)
    exit_keyboard = KeyboardButton(strings_const.EXIT_TEXT)

    keyboards_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboards_menu.add(send_bug_report_keyboard).add(help_keyboard)
    # keyboards_menu.add(support_keyboard)
    keyboards_menu.add(exit_keyboard)

    await message.answer(strings_const.INFORMATION_TEXT, reply_markup=keyboards_menu)


@dp.message_handler(lambda message: message.text == strings_const.SUPPORT_TEXT, state='*')
async def get_support_information(message: types.Message):
    await message.answer(strings_const.SUPPORT_INFO_TEXT)


@dp.message_handler(lambda message: message.text == strings_const.HELP_LINK_TEXT, state='*')
async def get_link_help(message: types.Message):
    await get_help_menu(message)


@dp.message_handler(lambda message: message.text == strings_const.SEND_BUG_REPORT_TEXT, state='*')
async def send_bug_report(message: types.Message):
    await user_worker.send_bug_report(message)


@dp.message_handler(lambda message: message.text == strings_const.EXIT_TEXT, state='*')
async def exit(message: types.Message):
    await start(message)


if __name__ == '__main__':
    from user_worker import dp

    @dp.message_handler()
    async def any_command(message : types.Message):
        '''Функция непредсказумогого ответа'''
        await message.answer('Хм, незнаю что с этим делать\nПопробуй команду /help')

    @dp_tech_pause.message_handler()
    async def any_text(message: types.Message):
        await message.answer(strings_const.TECH_PAUSE)

    if config.TECH_PAUSE:
        executor.start_polling(dp_tech_pause, skip_updates=True)
    else:
        executor.start_polling(dp, skip_updates=True)

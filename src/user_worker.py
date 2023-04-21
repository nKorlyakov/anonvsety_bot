# Файл инкапсулирует в себе функционал для обычных пользователей
import asyncio
from random import randint
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, ChatIdIsEmpty

from sqlalchemy import desc

import strings_const
from main import dp, bot, start, session, logger
from database_worker import Message as MessageDB
import database_worker as db
import config
import utils


class CompanionGroup:
    '''
    Класс в котором находятся собеседники во время чатинга
    Берет на себя роль очереди и роутинга получателя сообщений
    '''
    def __init__(self):
        self.companion_groups = dict()

    def add_new_companion(self, telegram_id_user: int) -> None:
        '''
        Добавляет нового собеседника в очередь
        '''
        self.companion_groups[telegram_id_user] = None

    def is_blank_companion(self, telegram_id_user: int) -> int | bool:
        '''
        Функция возвращает telegram id юзера без собеседника
        В ином случае кидает False
        '''
        try:
            result = list(self.companion_groups.keys())
            return result[list(self.companion_groups.values()).index(None)] if result[list(self.companion_groups.values()).index(None)] != telegram_id_user \
                                                                            else result[list(self.companion_groups.values()).index(None)]
        except ValueError:
            return False

    def add_new_companions(self, telegram_id_user_sender: int, telegram_id_user_receiver: int) -> None:
        '''
        Добавляет новую пару собеседников
        '''
        self.companion_groups[telegram_id_user_receiver] = telegram_id_user_sender
        self.companion_groups[telegram_id_user_sender] = telegram_id_user_receiver

    def del_companions(self, telegram_id_user: int) -> None:
        '''
        Удаляет пару собеседников
        '''
        try:
            del self.companion_groups[self.companion_groups[telegram_id_user]]
        except KeyError:
            pass
        try:
            del self.companion_groups[telegram_id_user]
        except KeyError:
            pass

    def get_companion(self, telegram_id_user: int) -> int | bool:
        try:
            return self.companion_groups[telegram_id_user]
        except KeyError:
            return False


class Chating(StatesGroup):
    '''
    Класс для работы с SFM во время чатинга двух собеседников
    '''
    message_sending = State()
    # TODO
    report = State()

    commands = [strings_const.STOP_TEXT,
                strings_const.SHARE_LINK_TEXT,
                strings_const.COIN_FLIP_TEXT]
    chating_keyboard_menu = ReplyKeyboardMarkup([[KeyboardButton(command)] for command in commands], resize_keyboard=True)

    commands_end = [strings_const.NEXT_COMPANION_TEXT,
                    strings_const.EXIT_TEXT]
    dialog_end_menu = ReplyKeyboardMarkup([[KeyboardButton(command_end)] for command_end in commands_end], resize_keyboard=True)


class Message:
    '''
    Класс который инкапсулирует в себе логику работы с сообщениями
    пользователей перед загрузкой их на бд(чтобы уменьшить нагрузку на эту самую бд)'''
    def __init__(self):
        self.messages: dict = dict()

    def add_message(self, sender_telegram_id: int, receiver_telegram_id: int, message: str) -> None:
        try:
            self.messages[sender_telegram_id]['messages'].append(message)
        except KeyError:
            self.messages[sender_telegram_id] = {'sender': sender_telegram_id, 'receiver': receiver_telegram_id, 'messages': [message]}

    def get_all_messages_from_dialog(self, first_telegram_id: int, second_telegram_id: int) -> list:
        '''
        Функция возвращает все сообщения из диалога
        '''
        try:
            first_user_messages = self.messages[first_telegram_id]
        except KeyError:
            first_user_messages = {}
        try:
            second_user_messages = self.messages[second_telegram_id]
        except KeyError:
            second_user_messages = {}

        return [first_user_messages, second_user_messages]

    def get_all_messages_from_dialog_from_user(self, telegram_id_user: int) -> list:
        '''
        Функция возвращает сообщения определенного юзера
        '''
        try:
            user_messages = self.messages[telegram_id_user]
        except KeyError:
            user_messages = {}

        return user_messages

    def delete_messages_from_dialog(self, first_telegram_id: int, second_telegram_id: int) -> None:
        '''
        Удаляет все сообщения диалога между двумя юзерами
        '''
        try:
            del self.messages[first_telegram_id]
        except KeyError:
            pass
        try:
            del self.messages[second_telegram_id]
        except KeyError:
            pass
    

companion_groups = CompanionGroup()
messages = Message()


async def search_companion(message: types.Message):
    ''' Функция реализация очереди в поиске собеседника '''
    try:
        if companion_groups.get_companion(message.from_user.id) is False:
            counter_loop = 0

            if not companion_groups.is_blank_companion(message.from_user.id):
                companion_groups.add_new_companion(message.from_user.id)
            else:
                companion_groups.add_new_companions(companion_groups.is_blank_companion(message.from_user.id), message.from_user.id)

            logger.send_to_file(f'New member of queue - {message.from_user.id}', 'INFO')
                
            while companion_groups.is_blank_companion(message.from_user.id):
                # counter_loop - счетчик итераций ожидания, 1 - 0.2 секунды
                if counter_loop == 1:
                    await message.answer(strings_const.START_SEARCH)
                if counter_loop == 20:
                    await message.answer(strings_const.WAIT_MORE_2_SEC_TEXT)
                if counter_loop == 20000:
                    await message.answer(strings_const.NOBODY_FOUND)
                    companion_groups.del_companions(message.from_user.id)
                    return
                await asyncio.sleep(0.2)
                counter_loop += 1

            await Chating.message_sending.set()
            await message.answer(strings_const.END_SEARCH, reply_markup=Chating.chating_keyboard_menu)
            logger.send_to_file(f'New pair of queue - {message.from_user.username if message.from_user.username else message.from_user.id} : {companion_groups.get_companion(message.from_user.id)}', 'INFO')
        else:
            await message.answer(strings_const.ALREADY_SEARCH_TEXT)
    except Exception as error:
        logger.send_to_file(error, 'ERROR')


@dp.message_handler(state=Chating.message_sending, content_types=ContentType.ANY)
async def send_message_companion(message, state):
    ''' Функция роутер сообщений пользователя пользователю в диалоге '''
    try:
        if message.content_type != 'text':
            try:
                match message.content_type:
                    case 'photo':
                        await bot.send_photo(companion_groups.get_companion(message.from_user.id), 
                                            photo=message.photo[-1].file_id, caption=message.caption if message.caption else None)
                        await message.photo[-1].download(f'../user_content/pictures/{message.from_user.id}_{message.photo[-1].file_unique_id}.jpg')
                    case 'sticker':
                        await bot.send_sticker(companion_groups.get_companion(message.from_user.id), sticker=message.sticker.file_id)
                    case 'video':
                        await bot.send_video(companion_groups.get_companion(message.from_user.id), message.video.file_id)
                        await message.video.download(f'../user_content/videos/{message.from_user.id}_{message.video.file_unique_id}.mp4') 
                    case 'document':
                        await bot.send_document(companion_groups.get_companion(message.from_user.id), message.document.file_id)
                    case 'voice':
                        await bot.send_voice(companion_groups.get_companion(message.from_user.id), message.voice.file_id)
                        await message.voice.download(f'../user_content/voices/{message.from_user.id}_{message.voice.file_unique_id}.mp3') 
                    case 'video_note':
                       await bot.send_video_note(companion_groups.get_companion(message.from_user.id), message.video_note.file_id)
                       await message.video_note.download(f'../user_content/video_notes/{message.from_user.id}_{message.video_note.file_unique_id}.mp4')
                logger.send_to_file(f'New file from user {message.from_user.username if message.from_user.username else message.from_user.id} - {message.content_type}')
            except ChatNotFound:
                pass
                    
        else:
            logger.send_to_file(f'New message from user {message.from_user.username if message.from_user.username else message.from_user.id} - {message.text}', 'INFO')
            match message.text:
                case strings_const.STOP_TEXT:
                    # Оповещение о конце диалога
                    await message.answer(strings_const.DIALOG_END, reply_markup=Chating.dialog_end_menu)
                    await bot.send_message(companion_groups.get_companion(message.from_user.id), strings_const.DIALOG_END, reply_markup=Chating.dialog_end_menu)

                    # Добавление сообщений из диалога в бд
                    DATE_NOW = datetime.now()
                    messages_from_dialog = messages.get_all_messages_from_dialog(message.from_user.id, companion_groups.get_companion(message.from_user.id))
                    for messages_from_user in messages_from_dialog:
                        if messages_from_user:
                            for message_text in messages_from_user['messages']:
                                message_db = MessageDB(sender_id=messages_from_user['sender'],
                                                  receiver_id=messages_from_user['receiver'],
                                                  message_text=message_text,
                                                  creation_date=DATE_NOW)
                                session.add(message_db)
                                session.commit()

                    # Добавление рейтинга
                    first_user = session.query(db.User).filter(db.User.telegram_id == message.from_user.id).one_or_none()
                    second_user = session.query(db.User).filter(db.User.telegram_id == companion_groups.get_companion(message.from_user.id)).one_or_none()
                    try:
                        first_user.rating += len(messages.get_all_messages_from_dialog_from_user(message.from_user.id)['messages']) * 5
                    except KeyError:
                        pass
                    try:
                        second_user.rating += len(messages.get_all_messages_from_dialog_from_user(companion_groups.get_companion(message.from_user.id))['messages']) * 5
                    except KeyError:
                        pass
                    session.commit()

                    # rollback
                    messages.delete_messages_from_dialog(message.from_user.id, companion_groups.get_companion(message.from_user.id))
                    companion_groups.del_companions(message.from_user.id)
                case strings_const.SHARE_LINK_TEXT:
                    await bot.send_message(companion_groups.get_companion(message.from_user.id), strings_const.SHARE_LINK_TEMPLATE.substitute(username=message.from_user.username) if message.from_user.username is not None else "Пользователь не заполнил свой username", reply_markup=Chating.chating_keyboard_menu)
                case strings_const.COIN_FLIP_TEXT:
                    coin_flip: int = randint(1,2)
                    if coin_flip == 1:
                        coin_flip = 'Решка'
                    else:
                        coin_flip = 'Орёл'
                    await message.answer(strings_const.COIN_FLIP_TEMPLATE.substitute(coin_flip=coin_flip))
                    await bot.send_message(companion_groups.get_companion(message.from_user.id), strings_const.COIN_FLIP_TEMPLATE.substitute(coin_flip=coin_flip))
                case strings_const.EXIT_TEXT:
                    await state.finish()
                    await exit(message)
                case strings_const.NEXT_COMPANION_TEXT:
                    await search_companion(message)
                case _ :
                    try:
                        if message.text in (strings_const.COIN_FLIP_TEMPLATE.substitute(coin_flip='Решка'), strings_const.COIN_FLIP_TEMPLATE.substitute(coin_flip='Орёл')):
                            await bot.send_message(companion_groups.get_companion(message.from_user.id), strings_const.SCAM_TEMPLATE, reply_markup=Chating.chating_keyboard_menu)
                            await message.answer('Обманывать плохо!')
                        else:
                            await bot.send_message(companion_groups.get_companion(message.from_user.id), message.text, reply_markup=Chating.chating_keyboard_menu)
                            messages.add_message(message.from_user.id, companion_groups.get_companion(message.from_user.id), message.text)
                    except (KeyError, ChatNotFound, ChatIdIsEmpty):
                        await state.finish()
                        await start(message)
    except Exception as error:
        logger.send_to_file(error, 'ERROR') 


async def get_rating(message: types.Message):
    top5_rating: list = session.query(db.User).order_by(desc(db.User.rating)).limit(5).all()
    await message.answer(strings_const.RATING_TEMPLATE.substitute(users_rating='\n'.join([f'{user.first_name} - {user.rating} MMR' for user in top5_rating])))


async def exit(message: types.Message):
    await start(message)


async def get_profile(message: types.Message):
    profile = session.query(db.User).filter(db.User.telegram_id == message.from_user.id).one_or_none()

    if profile:
        time_delta: datetime.timedelta = datetime.now() - profile.creation_date
        all_messages_from_user = session.query(db.Message.receiver_id).filter(db.Message.sender_id == message.from_user.id).all()
        top5_rating: list = [x[0] for x in session.query(db.User.telegram_id).order_by(desc(db.User.rating)).limit(5).all()]
        try:
            additional_info = f'🏆 {top5_rating.index(message.from_user.id) + 1} место в топе рейтинга\n'
        except ValueError:
            additional_info = ''

        await message.answer(strings_const.PROFILE_TEMPLATE.substitute(id=profile.id, 
                                                                       days=time_delta.days, 
                                                                       hours=time_delta.seconds // 3600, 
                                                                       count_messages=len(all_messages_from_user),
                                                                       count_dialogs=len(set(all_messages_from_user)),
                                                                       rating_score=profile.rating,
                                                                       additional_info=additional_info
                                                                       ))


class BugReport(StatesGroup):
    '''
    Класс для работы с SFM для отправки баг репорта
    '''
    report_text = State()
    report_image = State()


async def send_bug_report(message: types.Message):
    await message.answer(strings_const.SEND_BUG_REPORT_WELCOME_TEXT, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(strings_const.EXIT_TEXT)))
    await BugReport.report_text.set()


@dp.message_handler(state=BugReport.report_text)
async def send_bug_report_text(message, state):
    try:
        if message.text == strings_const.EXIT_TEXT:
            await state.finish()
            await exit(message)
            return
        await state.update_data(report_text=message.text)
        await message.answer(strings_const.SEND_BUG_REPORT_IMAGE)
        await BugReport.next()
    except Exception as error:
        await state.finish()
        logger.send_to_file(error, 'ERROR')


@dp.message_handler(state=BugReport.report_image, content_types=ContentType.ANY)
async def send_bug_report_image(message, state):
    try:
        if message.content_type == 'photo':
            user_data = await state.get_data()
            await bot.send_photo(config.LOG_CHANNEL_ID, photo=message.photo[-1].file_id, caption=user_data['report_text'])
            await message.answer(strings_const.THANKS_FOR_BUG_REPORT_TEXT)
            await state.finish()
            await exit(message)
        else:
            await state.finish()
            await exit(message)
    except Exception as error:
        await state.finish()
        logger.send_to_file(error, 'ERROR')

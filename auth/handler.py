import hashlib
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
import querylist
from auth import help
from db import BotDB
from states import UserState

BotDB = BotDB("files.db")


# Проверка уровня доступа к функциям, возврат соотв. клавиатуры
async def access_level_check(message, **kwargs):
    access_level = await BotDB.get_stuff(querylist.access_query, **kwargs)
    if access_level == 1:
        await message.answer(text='Выберите команду:', reply_markup=keyboard.start_menu_merch)
        await UserState.auth.set()
    elif access_level == 2:
        await message.answer(text='Выберите команду:', reply_markup=keyboard.start_menu_super)
        await UserState.auth.set()
    elif access_level == 3:
        await message.answer(text='Выберите команду:', reply_markup=keyboard.start_menu_admin)
        await UserState.auth.set()
    else:
        await message.answer(text='Какая-то ошибка!')
        await UserState.auth.set()


# обработка команды start
async def start_message(message: types.Message):
    await message.answer("Привет!\n\nЯ бот-помощник компании Mars.\n\nДля начала работы введите личный пароль!\n\n"
                         "Если у вас нет личного пароля для доступа к боту - обратитесь к своему супервайзеру!")
    await UserState.new_user.set()


# обработка команды help
async def help_message(message: types.Message):
    await message.answer(help.help_message)


# обработка ввода пароля и проверка уровня доступа, если верный - записываем tg_id юзера в базу,
# получаем его ФИО из базы, проверяем уровень доступа
async def user_login(message: types.Message):
    password = hashlib.sha512(message.text.encode('utf-8')).hexdigest()
    data = await BotDB.get_check(querylist.check_query, password=password)
    if data:
        await BotDB.record_to_db(querylist.set_tg_id, tg_id=message.from_user.id, password=password)
        username = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
        await message.answer(text=f'Пароль верный!\n\nПриветствую вас,\n\n*{username}!*', parse_mode='Markdown')
        await access_level_check(message, password=password)
    else:
        await message.answer(text='Пароль неверный!')


# проверка на авторизацию и уровень доступа при отправке сообщения боту
async def check_auth(message: types.Message):
    data = await BotDB.get_check(querylist.check_query, tg_id=message.from_user.id)
    if data:
        await access_level_check(message, tg_id=message.from_user.id)
    else:
        await message.answer(text='Вы не авторизованы!\nНажмите /start')


# обработка команды logout, удаляем tg_id из базы
async def logout(message: types.Message, state: FSMContext):
    await BotDB.record_to_db(querylist.logout, tg_id=message.from_user.id)
    await message.answer(text='Вы успешно разлогинились!')
    await state.finish()


# компануем в обработчик
def register_handlers_auth(dp: Dispatcher):
    dp.register_message_handler(start_message, commands=['start'])
    dp.register_message_handler(help_message, commands=['help'])
    dp.register_message_handler(user_login, state=UserState.new_user)
    dp.register_message_handler(check_auth)
    dp.register_message_handler(check_auth, text="Назад", state='*')
    dp.register_message_handler(logout, commands=['logout'], state=UserState.auth)

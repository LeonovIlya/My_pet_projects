import aiosqlite
import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
import querylist
from db import BotDB
from states import UserState

BotDB = BotDB("files.db")


# клавиатура управления мерчами
async def manage_merchs(message: types.Message):
    await message.answer(text='Выберите команду:', reply_markup=keyboard.manage_merch)
    await UserState.supervisor.set()


# выбор функций поиска мерчей
async def search_merch(message: types.Message, state: FSMContext):
    if message.text == 'Поиск по ФИО':
        await message.answer(text='Функция в стадии разработки, выберите другую функцию!',
                             reply_markup=keyboard.manage_merch)
    elif message.text == 'Список моих мерчей':
        supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
        data = await BotDB.get_stuff_list(querylist.get_query, supervisor_name=supervisor_name)
        text = '\n'.join(data)
        await message.answer(text=text)
        await message.answer(text='Выберите команду:',
                             reply_markup=keyboard.manage_merch_next)
        await UserState.manage_merch.set()
    else:
        await message.answer(text='Какая-то ошибка!\nПопробуйте сначала!')
        await state.finish()


# выбор функций управления мерчами, запрашиваем ФИО
async def manage_merch(message: types.Message):
    if message.text == 'Добавить мерча':
        await message.answer(text='Введите полностью ФИО нового мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.add_merch_set_name.set()
    elif message.text == 'Удалить мерча':
        await message.answer(text='Введите полностью ФИО мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.delete_merch_set_name.set()
    elif message.text == 'Редактировать мерча':
        await message.answer(text='Введите полностью ФИО мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.edit_merch_set_name.set()


# получаем ФИО, запрашиваем пароль
async def add_merch_set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Введите пароль для нового мерчендайзера:')
    await UserState.add_merch_set_password.set()


# получаем пароль, записываем данные в БД, проверяем на уникальность
async def add_merch_set_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
    try:
        await BotDB.record_to_db(querylist.insert_user,
                                 name=data['name'], password=data['password'], supervisor_name=supervisor_name)

        await message.answer(text=f'Новый мерчендайзер *{data["name"]}* успешно добавлен!\n'
                                  f'Пароль: *{data["password"]}*', parse_mode='Markdown', reply_markup=keyboard.back)
        await state.finish()
    except aiosqlite.IntegrityError as error:
        await message.answer(text=f'*ОШИБКА!*\n\nМерчендайзер с таким ФИО или ПАРОЛЕМ уже есть в базе!',
                             parse_mode='Markdown',
                             reply_markup=keyboard.manage_merch_next)
        await UserState.manage_merch.set()
        logging.info(f'{error}')
    except Exception as error:
        await message.answer(text=f'*ОШИБКА!*\n{error}', parse_mode='Markdown',
                             reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем ФИО мерча, удаляем его из БД
async def delete_merch_set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await BotDB.record_to_db(querylist.delete_user, name=data['name'])
        await message.answer(text=f'Мерчендайзер *{data["name"]}* успешно удалён из базы!', parse_mode='Markdown',
                             reply_markup=keyboard.back)
        await state.finish()
    except Exception as error:
        await state.finish()
        logging.info(f'{error}')


# редактирование мерча
async def edit_merch_set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Выберите команду:', reply_markup=keyboard.edit_user)
    await UserState.edit_merch_choice.set()


# выбор информации для редактирования
async def edit_merch_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Изменить ФИО':
        await message.answer(text=f'Введите новые данные ФИО:\n(Например: Иванов Иван Иванович)\n\n'
                                  f'Текущие данные ФИО: *{data["name"]}*',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_merch_set_new_name.set()
    elif message.text == 'Изменить пароль':
        await message.answer(text=f'Введите новый пароль для *{data["name"]}* :',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_merch_set_new_password.set()


# редактирование имени, получаем новое, записываем в БД, проверяем на уникальность
async def edit_merch_set_new_name(message: types.Message, state: FSMContext):
    await state.update_data(new_name=message.text)
    data = await state.get_data()
    try:
        await BotDB.record_to_db(querylist.edit_user_name, new_name=data['new_name'], name=data['name'])
        await message.answer(text=f'ФИО успешно изменены!\n\n'
                                  f'Было: {data["name"]}\n'
                                  f'Стало: *{data["new_name"]}*',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await state.finish()
    except aiosqlite.IntegrityError as error:
        await message.answer(text=f'*ОШИБКА!*\n\nМерчендайзер с таким ФИО уже есть в базе!',
                             parse_mode='Markdown',
                             reply_markup=keyboard.manage_merch_next)
        await UserState.manage_merch.set()
        logging.info(f'{error}')
    except Exception as error:
        await message.answer(text=f'*ОШИБКА!*\n{error}', parse_mode='Markdown',
                             reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# редактирование пароля, получаем новый, записываем в БД, проверяем на уникальность
async def edit_merch_set_new_password(message: types.Message, state: FSMContext):
    await state.update_data(new_password=message.text)
    data = await state.get_data()
    try:
        await BotDB.record_to_db(querylist.edit_user_password, new_password=data['new_password'], name=data['name'])
        await message.answer(text=f'Пароль для *{data["name"]}* успешно изменён на *{data["new_password"]}*!\n\n',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await state.finish()
    except aiosqlite.IntegrityError as error:
        await message.answer(text=f'*ОШИБКА!*\n\nМерчендайзер с таким ПАРОЛЕМ уже есть в базе!',
                             parse_mode='Markdown',
                             reply_markup=keyboard.manage_merch_next)
        await UserState.manage_merch.set()
        logging.info(f'{error}')
    except Exception as error:
        await message.answer(text=f'*ОШИБКА!*\n{error}', parse_mode='Markdown',
                             reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# компануем в обработчик
def register_handlers_manage_merch(dp: Dispatcher):
    dp.register_message_handler(manage_merchs, text="Управление мерчами", state=UserState.auth)
    dp.register_message_handler(search_merch, state=UserState.supervisor)
    dp.register_message_handler(manage_merch, state=UserState.manage_merch)
    dp.register_message_handler(add_merch_set_name, state=UserState.add_merch_set_name)
    dp.register_message_handler(add_merch_set_password, state=UserState.add_merch_set_password)
    dp.register_message_handler(delete_merch_set_name, state=UserState.delete_merch_set_name)
    dp.register_message_handler(edit_merch_set_name, state=UserState.edit_merch_set_name)
    dp.register_message_handler(edit_merch_choice, state=UserState.edit_merch_choice)
    dp.register_message_handler(edit_merch_set_new_name, state=UserState.edit_merch_set_new_name)
    dp.register_message_handler(edit_merch_set_new_password, state=UserState.edit_merch_set_new_password)

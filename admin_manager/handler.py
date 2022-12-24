import hashlib
import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
import querylist
from db import BotDB
from states import UserState

BotDB = BotDB("files.db")


# клавиатура управления юзерами, проверяем наличие доступа к функции
async def manage_users(message: types.Message, state: FSMContext):
    access_level = await BotDB.get_stuff(querylist.access_query, tg_id=message.from_user.id)
    if access_level == 3:
        await message.answer(text='Выберите команду:', reply_markup=keyboard.manage_user)
        await UserState.admin.set()
    else:
        await message.answer(text='У вас нет прав для данной функции!', reply_markup=keyboard.back)
        await state.finish()


# выбор функций управления юзерами
async def select_functions(message: types.Message, state: FSMContext):
    if message.text == 'Добавить юзера':
        await message.answer(text='Введите полностью ФИО нового юзера:\n(Например: Иванов Иван Иванович)')
        await UserState.add_user_set_name.set()
    elif message.text == 'Удалить юзера':
        await message.answer(text='Введите полностью ФИО юзера:\n(Например: Иванов Иван Иванович)')
        await UserState.delete_user_set_name.set()
    elif message.text == 'Редактировать юзера':
        await message.answer(text='Введите полностью ФИО юзера:\n(Например: Иванов Иван Иванович)')
        await UserState.edit_user_set.set()
    elif message.text == 'Поиск по ФИО':
        await message.answer(text='Функция в стадии разработки, выберите другую функцию!',
                             reply_markup=keyboard.manage_user)
    elif message.text == 'Список всех юзеров':
        try:
            data = await BotDB.get_stuff_list(querylist.get_query_with_access)
            text = '\n'.join(list(map(" - ".join, data)))
            await message.answer(text=text)
            await message.answer(text='Уровни доступа: 1-мерч, 2-супер, 3-админ.', reply_markup=keyboard.manage_user)
        except Exception as error:
            await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
            await state.finish()
            logging.info(f'{error}')
    else:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()


# получаем ФИО, проверяем есть ли в БД, записывем, запрашиваем пароль
async def add_user_set_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            await message.answer(text='Юзер с таким ФИО уже есть в базе!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            await state.update_data(name=message.text)
            await message.answer(text='Введите уровень доступа нового юзера (цифра):'
                                      '\n1 - мерчендайзер\n2 - супервайзер\n3 - админ')
            await UserState.add_user_set_access_level.set()
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем и записываем уровень доступа, для мерча запрашиваем ФИО супервайзера, для остальных - пароль
async def add_user_set_access_level(message: types.Message, state: FSMContext):
    if message.text in ('1', '2', '3'):
        await state.update_data(access_level=message.text)
        if message.text == '1':
            try:
                data = await BotDB.get_stuff_list(querylist.get_query, access_level='2')
                await message.answer(text='Вы добавляете нового мерчендайзера,'
                                          ' необходимо указать ФИО его руководителя (супервайзера)!\n\n'
                                          'Спиcок супервайзеров:')
                text = '\n\n'.join(data)
                await message.answer(text=text)
                await UserState.add_user_supervisor_name.set()
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
        elif message.text == '2' or '3':
            await state.update_data(supervisor_name=None)
            await message.answer(text='Введите пароль для нового юзера:')
            await UserState.add_user_query.set()
    else:
        await message.answer(text='Введите верный уровень доступа!')


# получаем и записываем ФИО супервайзера, запрашиваем пароль
async def add_user_supervisor_name(message: types.Message, state: FSMContext):
    try:
        data = await BotDB.get_stuff_list(querylist.get_query, access_level='2')
        if message.text in data:
            await state.update_data(supervisor_name=message.text)
            await message.answer(text='Введите пароль для нового юзера:')
            await UserState.add_user_query.set()
        else:
            await message.answer(text='Вы ввели неверные ФИО супервайзера!\n\n'
                                      'Введите еще раз или нажмите кнопку назад!', reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем и записываем пароль, формируем запрос к БД, получаем ответ, обрабатываем ошибку если запись не уникальна
async def add_user_query(message: types.Message, state: FSMContext):
    password = hashlib.sha512(message.text.encode('utf-8')).hexdigest()
    try:
        if await BotDB.get_check(querylist.check_query, password=password):
            await message.answer(text='Пароль не уникален!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            try:
                data = await state.get_data()
                await BotDB.record_to_db(querylist.insert_user,
                                         name=data['name'], password=password,
                                         access_level=data['access_level'],
                                         supervisor_name=data['supervisor_name'])
                await message.answer(text=f'Новый юзер *{data["name"]}* добавлен!\n'
                                          f'Пароль: *{message.text}*\n'
                                          f'Уровень доступа: *{data["access_level"]}*\n'
                                          f'Супервайзер: *{data["supervisor_name"]}*',
                                     parse_mode='Markdown', reply_markup=keyboard.back)
                await state.finish()
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем ФИО юзера, проверяем на его наличие в БД, удаляем его из БД
async def delete_user_set_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            try:
                await BotDB.record_to_db(querylist.delete_user, name=message.text)
                await message.answer(text=f'Юзер *{message.text}* удалён из базы!', parse_mode='Markdown',
                                     reply_markup=keyboard.back)
                await state.finish()
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
        else:
            await message.answer(text='Юзер с таким ФИО не обнаружен!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# меню редактирование юзера
async def edit_user_set(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            await state.update_data(name=message.text)
            await message.answer(text='Выберите команду:', reply_markup=keyboard.admin_edit_user)
            await UserState.edit_user_choice.set()
        else:
            await message.answer(text='Юзер с таким ФИО не обнаружен!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# выбор информации для редактирования
async def edit_user_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Изменить ФИО':
        await message.answer(text=f'Введите новые данные ФИО:\n(Например: Иванов Иван Иванович)\n\n'
                                  f'Текущие данные ФИО: *{data["name"]}*',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_user_set_new_name.set()
    elif message.text == 'Изменить пароль':
        await message.answer(text=f'Введите новый пароль для *{data["name"]}* :',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_user_set_new_password.set()
    elif message.text == 'Изменить уровень доступа':
        await message.answer(text=f'Введите новый уровень доступа для *{data["name"]}* :'
                                  f'\n1 - мерчендайзер\n2 - супервайзер\n3 - админ',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_user_set_new_access_level.set()
    elif message.text == 'Изменить супервайзера':
        await message.answer(text=f'Введите ФИО супервайзера для *{data["name"]}* :',
                             parse_mode='Markdown', reply_markup=keyboard.back)
        await UserState.edit_user_set_new_supervisor.set()


# редактирование имени, получаем новое, записываем в БД, проверяем на уникальность
async def edit_user_set_new_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            await message.answer(text='Юзер с таким ФИО уже есть в базе!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            data = await state.get_data()
            await BotDB.record_to_db(querylist.edit_user_name, new_name=message.text, name=data['name'])
            await message.answer(text=f'ФИО успешно изменены!\n\n'
                                      f'Было: {data["name"]}\n'
                                      f'Стало: *{message.text}*',
                                 parse_mode='Markdown', reply_markup=keyboard.back)
            await state.finish()
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# редактирование пароля, получаем новый, записываем в БД, проверяем на уникальность
async def edit_user_set_new_password(message: types.Message, state: FSMContext):
    password = hashlib.sha512(message.text.encode('utf-8')).hexdigest()
    try:
        if await BotDB.get_check(querylist.check_query, password=password):
            await message.answer(text='Пароль не уникален!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            data = await state.get_data()
            await BotDB.record_to_db(querylist.edit_user_password, password=password, name=data['name'])
            await message.answer(text=f'Пароль для *{data["name"]}* изменён на *{message.text}*!\n\n',
                                 parse_mode='Markdown', reply_markup=keyboard.back)
            await state.finish()
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем уровень доступа, проверяем, записываем в БД
async def edit_user_set_new_access_level(message: types.Message, state: FSMContext):
    if message.text in ('1', '2', '3'):
        try:
            data = await state.get_data()
            await BotDB.record_to_db(querylist.edit_user_access_level, access_level=message.text,
                                     name=data['name'])
            await message.answer(text=f'Уровень доступа для *{data["name"]}* изменён на *{message.text}*!\n\n',
                                 parse_mode='Markdown', reply_markup=keyboard.back)
            await state.finish()
        except Exception as error:
            await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
            await state.finish()
            logging.info(f'{error}')
    else:
        await message.answer(text='Неверный уровень доступа!\n\nВведите еще раз или нажмите кнопку назад!',
                             reply_markup=keyboard.back)


# получаем ФИО супервайзера, проверяем, записываем в БД
async def edit_user_set_new_supervisor(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            data = await state.get_data()
            await BotDB.record_to_db(querylist.edit_user_supervisor, supervisor_name=message.text, name=data['name'])
            await message.answer(text=f'Супервайзер для *{data["name"]}* изменён на *{message.text}*!\n\n',
                                 parse_mode='Markdown', reply_markup=keyboard.back)
            await state.finish()
        else:
            await message.answer(text='Вы ввели неверные ФИО супервайзера!\n\n'
                                      'Введите еще раз или нажмите кнопку назад!', reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


async def manage_planograms(message: types.Message, state: FSMContext):
    await message.answer(text='Функция в стадии разработки, выберите другую функцию!',
                         reply_markup=keyboard.back)


# компануем в обработчик
def register_handlers_manage_users(dp: Dispatcher):
    dp.register_message_handler(manage_users, text='Управление юзерами', state=UserState.auth)
    dp.register_message_handler(manage_planograms, text='Управление планограммами', state=UserState.auth)
    dp.register_message_handler(select_functions, state=UserState.admin)
    dp.register_message_handler(add_user_set_name, state=UserState.add_user_set_name)
    dp.register_message_handler(add_user_set_access_level, state=UserState.add_user_set_access_level)
    dp.register_message_handler(add_user_supervisor_name, state=UserState.add_user_supervisor_name)
    dp.register_message_handler(add_user_query, state=UserState.add_user_query)
    dp.register_message_handler(delete_user_set_name, state=UserState.delete_user_set_name)
    dp.register_message_handler(edit_user_set, state=UserState.edit_user_set)
    dp.register_message_handler(edit_user_choice, state=UserState.edit_user_choice)
    dp.register_message_handler(edit_user_set_new_name, state=UserState.edit_user_set_new_name)
    dp.register_message_handler(edit_user_set_new_password, state=UserState.edit_user_set_new_password)
    dp.register_message_handler(edit_user_set_new_access_level, state=UserState.edit_user_set_new_access_level)
    dp.register_message_handler(edit_user_set_new_supervisor, state=UserState.edit_user_set_new_supervisor)

import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
import querylist
from db import BotDB
from states import UserState

BotDB = BotDB("files.db")


# клавиатура управления мерчами, проверяем наличие доступа к функции
async def manage_merchs(message: types.Message, state: FSMContext):
    access_level = await BotDB.get_stuff(querylist.access_query, tg_id=message.from_user.id)
    if access_level == 2:
        await message.answer(text='Выберите команду:', reply_markup=keyboard.manage_merch)
        await UserState.supervisor.set()
    else:
        await message.answer(text='У вас нет прав для данной функции!', reply_markup=keyboard.back)
        await state.finish()


# выбор функций поиска мерчей
async def search_merch(message: types.Message, state: FSMContext):
    if message.text == 'Добавить мерча':
        await message.answer(text='Введите полностью ФИО нового мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.add_merch_set_name.set()
    elif message.text == 'Удалить мерча':
        await message.answer(text='Введите полностью ФИО мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.delete_merch_set_name.set()
    elif message.text == 'Редактировать мерча':
        await message.answer(text='Введите полностью ФИО мерчендайзера:\n(Например: Иванов Иван Иванович)')
        await UserState.edit_merch_set_name.set()
    elif message.text == 'Поиск по ФИО':
        await message.answer(text='Функция в стадии разработки, выберите другую функцию!',
                             reply_markup=keyboard.manage_merch)
    elif message.text == 'Список моих мерчей':
        try:
            supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
            data = await BotDB.get_stuff_list(querylist.get_query,
                                              supervisor_name=supervisor_name, access_level='1')
            text = '\n'.join(data)
            await message.answer(text=text, reply_markup=keyboard.manage_merch)
        except Exception as error:
            await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
            await state.finish()
            logging.info(f'{error}')
    else:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()


# получаем ФИО, запрашиваем пароль
async def add_merch_set_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            await message.answer(text='Юзер с таким ФИО уже есть в базе!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            await state.update_data(name=message.text)
            await message.answer(text='Введите пароль для нового мерчендайзера:')
            await UserState.add_merch_set_password.set()
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем пароль, записываем данные в БД, проверяем на уникальность
async def add_merch_set_password(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, password=message.text):
            await message.answer(text='Пароль не уникален!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            try:
                data = await state.get_data()
                supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
                await BotDB.record_to_db(querylist.insert_user,
                                         name=data['name'], password=message.text, access_level='1',
                                         supervisor_name=supervisor_name)

                await message.answer(text=f'Новый мерчендайзер *{data["name"]}* добавлен!\n'
                                          f'Пароль: *{message.text}*', parse_mode='Markdown',
                                     reply_markup=keyboard.back)
                await state.finish()
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# получаем ФИО мерча, удаляем его из БД
async def delete_merch_set_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            try:
                supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
                if await BotDB.get_check(querylist.check_query, name=message.text, supervisor_name=supervisor_name):
                    try:
                        await BotDB.record_to_db(querylist.delete_user, name=message.text)
                        await message.answer(text=f'Мерчендайзер *{message.text}* удалён из базы!',
                                             parse_mode='Markdown', reply_markup=keyboard.back)
                        await state.finish()
                    except Exception as error:
                        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                        await state.finish()
                        logging.info(f'{error}')
                else:
                    await message.answer(text='Данный мерчендайзер числится за другим супервайзером!'
                                              '\n\nВведите еще раз или нажмите кнопку назад!',
                                         reply_markup=keyboard.back)
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
        else:
            await message.answer(text='Мерчендайзер с таким ФИО не обнаружен!'
                                      '\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# редактирование мерча
async def edit_merch_set_name(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            try:
                supervisor_name = await BotDB.get_stuff(querylist.get_query, tg_id=message.from_user.id)
                if await BotDB.get_check(querylist.check_query, name=message.text, supervisor_name=supervisor_name):
                    await state.update_data(name=message.text)
                    await message.answer(text='Выберите команду:', reply_markup=keyboard.edit_user)
                    await UserState.edit_merch_choice.set()
                else:
                    await message.answer(text='Данный мерчендайзер числится за другим супервайзером!'
                                              '\n\nВведите еще раз или нажмите кнопку назад!',
                                         reply_markup=keyboard.back)
            except Exception as error:
                await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
                await state.finish()
                logging.info(f'{error}')
        else:
            await message.answer(text='Мерчендайзер с таким ФИО не обнаружен!'
                                      '\n\nВведите еще раз или нажмите кнопку назад!', reply_markup=keyboard.back)
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


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
    try:
        if await BotDB.get_check(querylist.check_query, name=message.text):
            await message.answer(text='Мерчендайзер с таким ФИО уже есть в базе!'
                                      '\n\nВведите еще раз или нажмите кнопку назад!',
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
async def edit_merch_set_new_password(message: types.Message, state: FSMContext):
    try:
        if await BotDB.get_check(querylist.check_query, password=message.text):
            await message.answer(text='Пароль не уникален!\n\nВведите еще раз или нажмите кнопку назад!',
                                 reply_markup=keyboard.back)
        else:
            data = await state.get_data()
            await BotDB.record_to_db(querylist.edit_user_password, new_password=message.text, name=data['name'])
            await message.answer(text=f'Пароль для *{data["name"]}* изменён на *{message.text}*!\n\n',
                                 parse_mode='Markdown', reply_markup=keyboard.back)
            await state.finish()
    except Exception as error:
        await message.answer(text='ОШИБКА!', reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# компануем в обработчик
def register_handlers_manage_merch(dp: Dispatcher):
    dp.register_message_handler(manage_merchs, text="Управление мерчами", state=UserState.auth)
    dp.register_message_handler(search_merch, state=UserState.supervisor)
    dp.register_message_handler(add_merch_set_name, state=UserState.add_merch_set_name)
    dp.register_message_handler(add_merch_set_password, state=UserState.add_merch_set_password)
    dp.register_message_handler(delete_merch_set_name, state=UserState.delete_merch_set_name)
    dp.register_message_handler(edit_merch_set_name, state=UserState.edit_merch_set_name)
    dp.register_message_handler(edit_merch_choice, state=UserState.edit_merch_choice)
    dp.register_message_handler(edit_merch_set_new_name, state=UserState.edit_merch_set_new_name)
    dp.register_message_handler(edit_merch_set_new_password, state=UserState.edit_merch_set_new_password)

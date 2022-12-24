from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
from states import UserState
from dmp.dmp import get_sheets_name, get_sheet_by_name, get_sheet_by_number
from auth.handler import check_auth


# получаем клавиатуру с выбором действий
async def dmp_start(message: types.Message):
    await message.answer(text='Идёт поиск доступных торговых сетей...')
    data = get_sheets_name()
    await message.answer(text='Выберите торговую сеть:', reply_markup=keyboard.get_list_inline(data))
    await UserState.dmp.set()


# выбираем действия, получаем список сетей
async def dmp_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(sheet_name=callback.data)
    await callback.message.answer(text='Выберите команду:', reply_markup=keyboard.dmp)


# получаем данные от пользователя название сети и поисковой запрос
async def dmp_set_method(message: types.Message):
    if message.text == 'Поиск по адресу':
        await message.answer('Введите название нас.пункта или улицы.\n'
                             'Можно вводить начальные буквы (например свобо вместо свободы):')
        await UserState.dmp_address_search.set()
    elif message.text == 'Поиск по коду ТТ':
        await message.answer('Введите номер ТТ:')
        await UserState.dmp_tt_search.set()


# обрабатываем запрос по адресу и выдаем данные
async def dmp_get_address(message: types.Message, state: FSMContext):
    if message.text.isalpha() and message.text != 'Назад':
        await message.answer(text='Идёт поиск в базе данных...')
        await state.update_data(query=message.text.lower())
        data = await state.get_data()
        query_list = get_sheet_by_name(data['sheet_name'], data['query'])
        if query_list:
            if isinstance(query_list, str):
                await message.answer(text=query_list, reply_markup=keyboard.back)
                await state.finish()
            else:
                text = '\n'.join(query_list)
                await message.answer(text=text, reply_markup=keyboard.back,  parse_mode='Markdown')
                await state.finish()
        else:
            await message.answer(text='Ничего не найдено!\n'
                                      'Введите запрос заного или нажмите кнопку назад.', reply_markup=keyboard.back)
    elif message.text == 'Назад':
        await state.finish()
        await check_auth(message)
    else:
        await message.answer(text='Неверный формат данных!\n Попробуйте еще раз!')


# обрабатываем запрос по номеру тт и выдаем данные
async def dmp_get_tt(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer(text='Идёт поиск в базе данных...')
        await state.update_data(query=message.text)
        data = await state.get_data()
        query_list = get_sheet_by_number(data['sheet_name'], data['query'])
        text = '\n'.join(query_list)
        if text:
            await message.answer(text=text, reply_markup=keyboard.back)
            await state.finish()
        else:
            await message.answer(text='Ничего не найдено!\n'
                                      'Введите запрос заного или нажмите кнопку назад.', reply_markup=keyboard.back)
    elif message.text == 'Назад':
        await state.finish()
        await check_auth(message)
    else:
        await message.answer(text='Неверный формат данных!\nВведите число!')


# компануем в обработчик
def register_handlers_dmp(dp: Dispatcher):
    dp.register_message_handler(dmp_start, text="ДМП", state=UserState.auth)
    dp.register_callback_query_handler(dmp_choice, state=UserState.dmp)
    dp.register_message_handler(dmp_set_method, state=UserState.dmp)
    dp.register_message_handler(dmp_get_address, state=UserState.dmp_address_search)
    dp.register_message_handler(dmp_get_tt, state=UserState.dmp_tt_search)

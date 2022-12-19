import logging
from pathlib import Path

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import keyboard
import querylist
from db import BotDB
from states import UserState

BotDB = BotDB("files.db")


# выбираем кластер
async def planogram_choice(message: types.Message):
    await message.answer(text='Выберите кластер:', reply_markup=keyboard.CLUSTERS_ALL)
    await UserState.plan_cluster.set()


# выбираем торговую сеть
async def cluster_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(cluster=callback.data)
    data = await BotDB.get_stuff_list(querylist.shop_list)
    await callback.message.answer(text='Выберите торговую сеть:',
                                  reply_markup=keyboard.get_list_inline(data))
    await UserState.plan_shop.set()


# выбираем формат магазина
async def shop_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == 'Магнит':
        data = await BotDB.get_stuff_list(querylist.magnit_list, chain_name=callback.data)
        await callback.message.answer(text='Выберите формат Магнита:',
                                      reply_markup=keyboard.get_list_inline(data))

    elif callback.data == 'Магнит ММ':
        data = await BotDB.get_stuff_list(querylist.name_query, shop_name=callback.data)
        await callback.message.answer(text='Выберите планограмму:',
                                      reply_markup=keyboard.get_list_inline(data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()

    elif callback.data == 'Магнит ГМ':
        data = await BotDB.get_stuff_list(querylist.name_query, shop_name=callback.data)
        await callback.message.answer(text='Выберите планограмму:',
                                      reply_markup=keyboard.get_list_inline(data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()

    elif callback.data == 'Магнит МК':
        data = await BotDB.get_stuff_list(querylist.name_query, shop_name=callback.data)
        await callback.message.answer(text='Выберите планограмму:',
                                      reply_markup=keyboard.get_list_inline(data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()
    else:
        data = await BotDB.get_stuff_list(querylist.name_query, shop_name=callback.data)
        await callback.message.answer(text='Выберите планограмму:',
                                      reply_markup=keyboard.get_list_inline(data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()


# формируем запрос к бд, получаем ответ
async def name_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    name = callback.data
    data = await state.get_data()
    try:
        await callback.message.answer(text='Делаю запрос в базу данных...')
        data = await BotDB.get_stuff(querylist.file_query, name=name, shop_name=data['shop_name'],
                                     cluster=data['cluster'])
        file = Path(data)
        if file.is_file():
            await callback.message.answer(text='Отправляю файл...')
            with open(data, 'rb') as file:
                await callback.message.answer_document(file, reply_markup=keyboard.back)
                await state.finish()
        else:
            await callback.message.answer(text='Файл не найден!', reply_markup=keyboard.back)
            await state.finish()
    except Exception as error:
        await callback.message.answer(text='Какая-то ошибка!\nПопробуйте сначала!\nError: %s' % error,
                                      reply_markup=keyboard.back)
        await state.finish()
        logging.info(f'{error}')


# компануем в обработчик
def register_handlers_planogram(dp: Dispatcher):
    dp.register_message_handler(planogram_choice, text="Планограммы", state=UserState.auth)
    dp.register_callback_query_handler(cluster_choice, state=UserState.plan_cluster)
    dp.register_callback_query_handler(shop_choice, state=UserState.plan_shop)
    dp.register_callback_query_handler(name_choice, state=UserState.plan_name)

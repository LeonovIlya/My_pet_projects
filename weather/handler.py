from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import keyboard
from weather.weather_api import get_weather
from states import UserState


# запрос геолоки
async def cmd_locate_me(message: types.Message):
    await message.answer(text='Для начала отправьте вашу геопозицию:', reply_markup=keyboard.send_location)


# получаем корды, обрабатываем, возвращаем результат
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    text = await get_weather(lat, lon)
    await message.answer(text=text, reply_markup=keyboard.back)
    await state.finish()


# компануем в обработчик
def register_handlers_weather(dp: Dispatcher):
    dp.register_message_handler(cmd_locate_me, text="Погода", state=UserState.auth)
    dp.register_message_handler(handle_location, content_types=['location'], state=UserState.auth)

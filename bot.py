import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


import config
from auth.hadler import register_handlers_auth
from weather.handler import register_handlers_weather
from dmp.handler import register_handlers_dmp
from planogram.handler import register_handlers_planogram
from sv_manager.handler import register_handlers_manage_merch


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(filename='bot_log.log',
                        filemode='a',
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", )
    logger.info("Starting bot")
    bot = Bot(token=config.TOKEN)
    try:
        logger.info(await bot.get_me())
    finally:
        await (await bot.get_session()).close()
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_weather(dp)
    register_handlers_auth(dp)
    register_handlers_dmp(dp)
    register_handlers_planogram(dp)
    register_handlers_manage_merch(dp)

    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

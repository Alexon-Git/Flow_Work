import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from core.settings import settings
from core.handlers import courier


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s")
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp = Dispatcher()


    dp.include_routers(courier.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())

    # запуск машины .\.venv\Scripts\activate 
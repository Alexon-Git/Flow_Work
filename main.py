import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from core.settings import settings
from core.handlers.basic import *
from core.handlers import courier
from core.handlers import customer


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s")
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp = Dispatcher()


    dp.message.register(start_command, Command(commands=['start']))
    dp.include_routers(courier.router,customer.router)

    asyncio.ensure_future(courier.check_date(bot))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    #asyncio.run(start())
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(start())
    loop.run_forever()
    # запуск машины .\.venv\Scripts\activate 
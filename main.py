import os
import logging
import asyncio
import datetime as dt
from aiogram import Bot, Dispatcher
from core.handlers.courier import scheduler
from core.settings import home
from core.handlers.basic import *
from core.administrate import router_admin
from core.handlers import main_router, courier

if not os.path.exists(f"{home}/logging"):
    os.makedirs(f"{home}/logging")

# Для отладки локально разкоментить
logging.basicConfig(level=logging.INFO)

# Для отладки локально закоментить
# logger = logging.getLogger()
# logger.setLevel(logging.WARNING)
# handler = logging.FileHandler(f"{home}/logging/bot{dt.date.today()}.log", "a+", encoding="utf-8")
# handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
# logger.addHandler(handler)
#
# logging.debug("Сообщения уровня DEBUG, необходимы при отладке ")
# logging.info("Сообщения уровня INFO, полезная информация при работе программы")
# logging.warning("Сообщения уровня WARNING, не критичны, но проблема может повторится")
# logging.error("Сообщения уровня ERROR, программа не смогла выполнить какую-либо функцию")
# logging.critical("Сообщения уровня CRITICAL, серьезная ошибка нарушающая дальнейшую работу")


async def start():
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp = Dispatcher()
    scheduler.start()
    scheduler.add_job(courier.check_date, "interval", seconds=21600, args=(bot,))
    # dp.message.register(start_command, Command(commands=['start']))
    dp.include_routers(main_router, router_admin)
    #asyncio.ensure_future(courier.check_date(bot))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # asyncio.ensure_future(start())
    # loop.run_forever()
    # запуск машины .\.venv\Scripts\activate

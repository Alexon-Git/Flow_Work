import os
import logging
import asyncio
import datetime as dt
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from core.settings import home, scheduler
from core.handlers.basic import *
from core.administrate import router_admin
from core.handlers import main_router, courier

if not os.path.exists(f"{home}/logging"):
    os.makedirs(f"{home}/logging")
if not os.path.exists(f"{home}/statistics/data"):
    os.makedirs(f"{home}/statistics/data")

# Для отладки локально разкоментить
# logging.basicConfig(level=logging.INFO)
#
# #Для отладки локально закоментить
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(f"{home}/logging/bot{dt.date.today()}.log", "a+", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

logging.debug("Сообщения уровня DEBUG, необходимы при отладке ")
logging.info("Сообщения уровня INFO, полезная информация при работе программы")
logging.warning("Сообщения уровня WARNING, не критичны, но проблема может повторится")
logging.error("Сообщения уровня ERROR, программа не смогла выполнить какую-либо функцию")
logging.critical("Сообщения уровня CRITICAL, серьезная ошибка нарушающая дальнейшую работу")


async def start():
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    REDIS_DSN = "redis://127.0.0.1:6379"
    storage = RedisStorage.from_url(REDIS_DSN, key_builder=DefaultKeyBuilder(with_bot_id=True),
                                    data_ttl=timedelta(days=1.0), state_ttl=timedelta(days=1.0))
    dp = Dispatcher(storage=storage)
    dp.include_routers(main_router, router_admin)
    dp.message.filter(F.chat.type == 'private')
    scheduler.start()
    scheduler.add_job(courier.check_date, "interval", seconds=21600)
    # dp.message.register(start_command, Command(commands=['start']))
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

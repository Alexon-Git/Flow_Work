from aiogram import Router

from .courier import router as cour
from .customer import router as cust
from .basic import router as bas

main_router = Router()

main_router.include_routers(cour, cust, bas)

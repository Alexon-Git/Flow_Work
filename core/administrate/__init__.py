import asyncio
from aiogram import Router, F

from .administrete import router as adm
from .edit_records import subrouter as edit
from .notification import subrouter as notif
from .cancel_state import subrouter as cst
from core.database.database import get_id_admin
router_admin = Router()
router_admin.include_routers(adm, edit, notif, cst)

loop = asyncio.get_event_loop()
result = loop.run_until_complete(get_id_admin())
router_admin.message.filter(F.from_user.id.in_(result))
router_admin.callback_query.filter(F.from_user.id.in_(result))

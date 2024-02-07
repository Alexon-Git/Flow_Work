from aiogram import Router

from .administrete import router as adm
from .edit_records import subrouter as edit
from .notification import subrouter as notif

router_admin = Router()
router_admin.include_routers(adm, edit, notif)

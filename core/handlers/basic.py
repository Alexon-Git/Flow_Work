from aiogram.types import Message

from core.keyboards.inline import *
from core.database import database
from core.message.text import get_text_start_mess

async def start_command(message: Message): # привет
    builder = create_start_buttons(message.from_user.id)
    await message.answer(get_text_start_mess(), reply_markup=builder.as_markup())
    if not(await database.check_user(user_id=message.from_user.id)):
        await database.set_new_user(user_id=message.from_user.id, username=message.from_user.first_name)
 



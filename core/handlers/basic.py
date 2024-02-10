from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter

from core.keyboards.inline import *
from core.database import database
from core.message.text import get_text_start_mess
from core.administrate.administrete import check_code_admin

router = Router()
 

@router.message(CommandStart(), StateFilter(None))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    try:
        if check_code_admin(int(message.text.split(" ")[-1])):
            await message.answer("Поздравляю, вы стали администратором!")
            await database.save_new_admin(message.from_user.id)
            return
    except:
        pass
    builder = await create_start_buttons(message.from_user.id)
    await message.answer(get_text_start_mess(), reply_markup=builder.as_markup())
    if not (await database.check_user(user_id=message.from_user.id)):
        await database.set_new_user(user_id=message.from_user.id, username=message.from_user.first_name)
    return


@router.callback_query(F.data == "start", StateFilter(None))
async def start_call_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    builder = await create_start_buttons(call.from_user.id)
    await call.message.edit_text(get_text_start_mess(), reply_markup=builder.as_markup())
    return


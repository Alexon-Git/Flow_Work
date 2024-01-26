from aiogram import Router, types,F,Bot
from aiogram.filters import Command,CommandStart, BaseFilter
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.keyboards.inline import *
from core.keyboards.reply import *
import database

router = Router()

@router.message(CommandStart)
async def start(message: Message):
    builder = create_start_buttons()
    await message.answer("Приветственное сообщение", reply_markup=builder.as_markup())
    if not(await database.check_user(user_id = message.from_user.id)):
        await database.set_new_user(user_id= message.from_user.id,username= message.from_user.first_name)

@router.callback_query(F.data=="courier")
async def courier_callback(callback: types.CallbackQuery,state: FSMContext):
    if await database.check_courier(user_id = callback.from_user.id):
        builder = create_courier_buttons(True) 
        message = "Меню для курьеров. У вас осталось N количество дней."
    else:
        message = "Меню для курьеров. Пройдите регистрацию и вы получите 14д. пробного периода."
        builder = create_courier_buttons(False)
    await callback.message.edit_text(text= message,reply_markup=builder.as_markup())
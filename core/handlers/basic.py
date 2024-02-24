from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
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


#===================================Обращение в поддержку===================================
class SupportQuestion(StatesGroup):
    SetQuestion = State()


@router.callback_query(F.data == "support")
async def support_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
    msg = await call.message.edit_text("Напишите свой вопрос или подробно опишите возникшую проблему:",
                                 reply_markup=custom_btn("Отмена", "start"))
    await state.set_state(SupportQuestion.SetQuestion)
    await state.update_data({"del": msg.message_id})


@router.message(SupportQuestion.SetQuestion)
async def support_chat(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data["del"], reply_markup=None)
    except:
        pass
    await state.update_data({"text": mess.text})
    await mess.answer("Проверьте свой вопрос перед отправкой:\n\n"
                      f"{mess.text}", reply_markup=confirmation(canc_data="start"))


@router.callback_query(F.data == "yes", SupportQuestion.SetQuestion)
async def support_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
    data_state = await state.get_data()
    await bot.send_message(settings.bots.chat_id,
                           f"Пользователь:\n"
                           f"Имя: [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n"
                           f"Ссылка: @{call.from_user.username}\n"
                           f"Обращение:\n\n{data_state['text']}", parse_mode="Markdown")
    await call.message.edit_text("Сообщение отправлено!")
    await state.clear()

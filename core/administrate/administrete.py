import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import StateFilter

from core.settings import settings, home, check_city
from core.keyboards import inline as kbi
from core.database.database import get_id_admin, get_data_admin, deleted_admin, get_user, get_all_price
from core.message.text import get_text_start_mess, set_text_start_mess, get_amount, set_amount, get_bet, set_bet

router = Router()

bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
class EditStartMess(StatesGroup):
    CheckOldMess = State()
    SetMessage = State()


@router.callback_query(F.data == "no", EditStartMess.CheckOldMess)
@router.callback_query(F.data == "admin")
async def menu_admins(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Доступные процессы:", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# ############################ Изменить стартовое сообщение ############################ #
@router.callback_query(F.data == "edit_start_mess")
async def check_start_mess(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Сейчас сообщение выглядит так:\n\n{get_text_start_mess()}\n\n"
                                 "Желаете изменить его?", reply_markup=kbi.confirmation())
    await state.set_state(EditStartMess.CheckOldMess)


@router.callback_query(F.data == "yes", EditStartMess.CheckOldMess)
@router.callback_query(F.data == "no", EditStartMess.SetMessage)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новое сообщение:", reply_markup=kbi.cancel())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditStartMess.SetMessage)


@router.message(F.photo, EditStartMess.SetMessage)
async def answer_to_photo(mess: Message):
    await mess.answer("Нельзя установить фотографию! Отправьте только текст!")


@router.message(EditStartMess.SetMessage)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except:
        pass
    await state.update_data({"text": mess.html_text})
    await mess.answer(f"Новое сообщение выглядит теперь так:\n\n{mess.html_text}\n\nСохраняем?",
                      reply_markup=kbi.confirmation())


@router.callback_query(F.data == "yes", EditStartMess.SetMessage)
async def save_new_start_mess(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    set_text_start_mess(data["text"])
    await call.message.edit_text("Новое сообщение сохранено!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# ############################ Изменить стоимость подписки ############################ #
class EditAmount(StatesGroup):
    CheckOldAmount = State()
    SetAmount = State()


@router.callback_query(F.data == "edit_amount")
async def check_amount(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Стоимость подписки на данный момент: {get_amount()/100}\n"
                                 "Желаете изменить её?", reply_markup=kbi.confirmation())
    await state.set_state(EditAmount.CheckOldAmount)


@router.callback_query(F.data == "yes", EditAmount.CheckOldAmount)
@router.callback_query(F.data == "no", EditAmount.SetAmount)
async def set_new_amount(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новую стоимость числом:", reply_markup=kbi.cancel())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditAmount.SetAmount)


@router.message(EditAmount.SetAmount)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        new_amount = int(mess.text)
        try:
            del_kb = (await state.get_data())["del"]
            await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
        except:
            pass
        await state.update_data({"amount": new_amount})
        await mess.answer(f"Новая стоимость: {new_amount}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    except:
        await mess.answer("Данные не являются числом или содержат лишние символы!", reply_markup=kbi.cancel())


@router.callback_query(F.data == "yes", EditAmount.SetAmount)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    set_amount(data["amount"]*100)
    await call.message.edit_text("Новая стоимость сохранена!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


# #############################################################################3 #
@router.callback_query(F.data == "add_admin")
async def add_admin(call: CallbackQuery, bot: Bot):
    await call.message.edit_text("Отправьте новому администратору ссылку:\n"
                                 f"https://t.me/{(await bot.me()).username}?start={call.message.message_id}")
    with open(f"{home}/administrate/code.txt", "w") as f:
        f.write(str(call.message.message_id))


def check_code_admin(code_in: int) -> bool:
    with open(f"{home}/administrate/code.txt", "r+") as f:
        try:
            saved_code = int(f.read())
        except:
            return False
        f.write("a")
    return saved_code == code_in


@router.callback_query(F.data.split("_")[0] == "no", StateFilter(None))
@router.callback_query(F.data == "del_admin")
async def del_admin(call: CallbackQuery):
    await call.message.edit_text("Выберите кого удаляем:", reply_markup=kbi.del_admin(await get_data_admin()))


@router.callback_query(F.data.split("_")[0] == "del", StateFilter(None))
async def del_admin(call: CallbackQuery):
    name = await get_user(int(call.data.split('_')[-1]))
    await call.message.edit_text(f"Вы уверены в удалении {name['username']}:",
                                 reply_markup=kbi.confirmation(cd_y=f"Yes_{call.data.split('_')[-1]}"))


@router.callback_query(F.data.split("_")[0] == "yes", StateFilter(None))
async def del_admin(call: CallbackQuery):
    await deleted_admin(int(call.data.split("_")[-1]))
    await call.message.edit_text("Администратор удален!", reply_markup=kbi.admin_menu(call.from_user.id))


# #################################### Мин и сред ставка######################################### #
class EditBet(StatesGroup):
    SetAmount = State()


@router.callback_query(F.data == "bet")
async def check_bet(call: CallbackQuery, state: FSMContext):
    list_price = await get_all_price()
    average = round(sum(list_price) / len(list_price))
    await call.message.edit_text(f"Минимальная установленная цена: {get_bet()}\n"
                                 f"Средняя цена на данный момент: {average}",
                                 reply_markup=kbi.edit_bet())


@router.callback_query(F.data == "bet_edit")
@router.callback_query(F.data == "no", EditAmount.SetAmount)
async def set_new_bet(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новую стоимость числом:", reply_markup=kbi.cancel())
    await state.update_data({"del": msg.message_id})
    await state.set_state(EditAmount.SetAmount)


@router.message(EditAmount.SetAmount)
async def check_new_mess(mess: Message, state: FSMContext, bot: Bot):
    try:
        new_amount = int(mess.text)
        try:
            del_kb = (await state.get_data())["del"]
            await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
        except:
            pass
        await state.update_data({"amount": new_amount})
        await mess.answer(f"Новая стоимость: {new_amount}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    except ValueError:
        await mess.answer("Данные не являются числом или содержат лишние символы!", reply_markup=kbi.cancel())


@router.callback_query(F.data == "yes", EditAmount.SetAmount)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    set_bet(data["amount"])
    await call.message.edit_text("Новая стоимость сохранена!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


@router.callback_query(F.data == "update_city")
async def update_city(call: CallbackQuery):
    await check_city()
    await call.answer("Список городов обновлен!")


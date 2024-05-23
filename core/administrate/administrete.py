import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from core.settings import settings, home, city_info
from core.keyboards import inline as kbi
from core.database.database import get_data_admin, deleted_admin, get_user, get_all_price
from core.message.text import get_text_start_mess, set_text_start_mess, get_amount, set_amount, get_bet, set_bet
from core.database import database
from aiogram.methods.get_chat import GetChat

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
    msg = await call.message.edit_text(f"Отправьте новое сообщение:", reply_markup=kbi.cancel_admin())
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
                                 "Желаете изменить её?", reply_markup=kbi.confirmation(cd_n="admin"))
    await state.set_state(EditAmount.CheckOldAmount)


@router.callback_query(F.data == "yes", EditAmount.CheckOldAmount)
@router.callback_query(F.data == "no", EditAmount.SetAmount)
async def set_new_amount(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новую стоимость числом:", reply_markup=kbi.cancel_admin())
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

        if new_amount < 100:
            msg = await mess.answer("Нельзя установить значение меньше 100р. Введите другую стоимость.", reply_markup=kbi.cancel_admin())
            await state.update_data({"del": msg.message_id})
            return
        await state.update_data({"amount": new_amount})
        await mess.answer(f"Новая стоимость: {new_amount}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    except:
        await mess.answer("Данные не являются числом или содержат лишние символы!", reply_markup=kbi.cancel_admin())


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
    try:
        average = round(sum(list_price) / len(list_price))
    except ZeroDivisionError:
        average = 0
    await call.message.edit_text(f"Минимальная установленная цена: {get_bet()}\n"
                                 f"Средняя цена на данный момент: {average}",
                                 reply_markup=kbi.edit_bet())


@router.callback_query(F.data == "bet_edit")
@router.callback_query(F.data == "no", EditAmount.SetAmount)
async def set_new_bet(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text(f"Отправьте новую стоимость числом:", reply_markup=kbi.cancel_admin())
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
        await state.update_data({"amount": new_amount*100})
        await mess.answer(f"Новая стоимость: {new_amount}\n\nСохраняем?",
                          reply_markup=kbi.confirmation())
    except ValueError:
        await mess.answer("Данные не являются числом или содержат лишние символы!", reply_markup=kbi.cancel_admin())


@router.callback_query(F.data == "yes", EditAmount.SetAmount)
async def set_new_start_mess(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    set_bet(data["amount"])
    await call.message.edit_text("Новая стоимость сохранена!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


@router.callback_query(F.data == "update_city")
async def update_city(call: CallbackQuery):
    city_info.update()
    await call.answer("Список городов обновлен!")


@router.callback_query(F.data == 'pinned_orders')
async def pinned_orders(callback: types.CallbackQuery, bot: Bot):
    list_pin_orders = await database.pinned_orders_request()
    status = ''
    if list_pin_orders is None:
        await callback.answer('Закрепленных заявок нет')
    for i in range(len(list_pin_orders)):
        courier_id = list_pin_orders[f'courier_id_{i}']
        chat_id = list_pin_orders[f'chat_id_{i}']
        status_db = list_pin_orders[f'status_work_{i}']
        user = await bot.get_chat(courier_id)
        name = user.username
        if status_db == 'work':
            status = 'Принят в работу'
        elif status_db == 'shop':
            status = 'Прибыл в магазин'
        elif status_db == 'get_order':
            status = 'Забрал заказ'
        elif status_db == 'arrived':
            status = 'Прибыл к получателю'
        code = list_pin_orders[f'code_{i}']
        msg = "<b>Закрепленная заявка</b>"
        msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        msg += f"Код: {list_pin_orders[f'code_{i}']}\n"
        msg += f"Ник: @{name}\n"
        msg += f"ID: {list_pin_orders[f'courier_id_{i}']}\n"
        msg += f"Магазин: {list_pin_orders[f'store_name_{i}']}\n"
        msg += f"Статус: {status}\n"
        adress_a = list_pin_orders[f'adress_a_{i}']
        adress_b = list_pin_orders[f'adress_b_{i}']
        msg += f"Адрес А:  <code>{adress_a}</code>\n"
        msg += f"Адрес Б:  <code>{adress_b}</code>\n"
        buttons = [
            [InlineKeyboardButton(text='Управление', callback_data=f"add_buttons {code}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                     reply_markup=markup)
        await callback.answer()

@router.callback_query(F.data.startswith('add_buttons'))
async def add_buttons(callback: CallbackQuery):
    code = callback.data.split()[1]
    buttons = [
        [InlineKeyboardButton(text='Время', callback_data=f"time_admin {code}")],
        [InlineKeyboardButton(text='Адрес A', callback_data=f"place_a_admin {code}")],
        [InlineKeyboardButton(text='Адрес B', callback_data=f"place_b_admin {code}")],
        [InlineKeyboardButton(text='Стоимость', callback_data=f"money_admin {code}")],
        [InlineKeyboardButton(text='Телефон заказчика', callback_data=f"phone_customer {code}")],
        [InlineKeyboardButton(text='Телефон исполнителя', callback_data=f"phone_executor {code}")],
        [InlineKeyboardButton(text='Переместить в активные', callback_data=f'admin_active {code}')],
        [InlineKeyboardButton(text='Передать заказ другому курьеру', callback_data=f'send_courier {code}')],
        [InlineKeyboardButton(text='Переместить в завершенные', callback_data=f'admin_close {code}')],
        [InlineKeyboardButton(text='Скрыть', callback_data=f'close_fixed {code}')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data.startswith('close_fixed'))
async def close_fixed(callback: CallbackQuery):
    code = callback.data.split()[1]
    button = [
        [InlineKeyboardButton(text='Управление', callback_data=f'add_buttons {code}')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    await callback.message.edit_reply_markup(reply_markup=keyboard)





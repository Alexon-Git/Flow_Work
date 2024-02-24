import math
import datetime
from datetime import date

from aiogram import Router, types, F, Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import LabeledPrice, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import StorageKey

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from core.keyboards.reply import *
from core.filters.Filters import *
from core.database import database
from core.keyboards.inline import *
from core.message.text import get_amount
from core.settings import check_city, city_info

router = Router()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


class CourierState(StatesGroup):
    fio = State()
    email = State()
    city = State()
    phone = State()
    n = ()


#===================================Меню Курьера===================================
@router.callback_query(F.data=="courier")
async def courier_callback(callback: types.CallbackQuery,bot:Bot):
    if await database.check_courier(user_id = callback.from_user.id):
        expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
        courier = await database.get_courier(callback.from_user.id)
        chat_id = 0
        for i in city_info:
            if i["Город"]==courier["city"]:
                chat_id = i["chat id"]
        link = await bot.create_chat_invite_link(chat_id=chat_id, expire_date= int( expire_date.timestamp()),member_limit= 1)
        builder = create_courier_buttons(True,link.invite_link) 
        
        days = datetime.datetime.strptime(courier["date_payment_expiration"], "%Y-%m-%d").date() - date.today()
        message = f"Меню для курьеров.\nУ вас осталось {days.days}д. оплаченной подписки."
    else:
        message = "Меню для курьеров.\nПройдите регистрацию и вы получите 14д. пробного периода."
        builder = create_courier_buttons(False)
    await callback.message.edit_text(text= message,reply_markup=builder.as_markup())



#===================================Колбек Меню Курьера===================================
@router.callback_query(F.data.startswith("courier_"))
async def courier_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    if action == "registration":
        await state.set_state(CourierState.fio)
        await callback.message.answer("Введите ваше ФИО")
        await callback.answer()
    #===================================ОПЛАТА===================================
    elif action == "payment":
        await bot.send_invoice(
        chat_id= callback.message.chat.id,
        title="Оплата подписки курьеров",
        description="Предоставляет возможность откликаться на заявки доставки",
        provider_token="381764678:TEST:77526",
        payload="bot",

        currency="rub",
        prices=[LabeledPrice(
            label = "Оплата подписки",
            amount=get_amount(),
            )],
        provider_data=None,
        is_flexible=False,
        request_timeout=10
        )
        await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery,bot:Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id,ok = True)

@router.message(F.successful_payment)
async def successful_payment(message:Message):
    courier = await database.get_courier(message.from_user.id)
    date = datetime.datetime.strptime(courier["date_payment_expiration"], "%Y-%m-%d").date() + datetime.timedelta(days=30)
    await database.payment_courier(message.from_user.id, str(date))
    await message.answer("Вы успешно оплатили подписку на месяц")

#===================================ФИО===================================
@router.message(CourierState.fio,FioFilter())
async def courier_fio(message: Message,state: FSMContext):
    await state.update_data(fio = message.text)
    await message.answer("Введите вашу почту")
    await state.set_state(CourierState.email)

@router.message(CourierState.fio)
async def fio_incorrectly(message: Message):
    await message.answer(
        text="Вы написали некорректное ФИО, повторите попытку.",
    )
    
    

#===================================Email===================================
@router.message(CourierState.email,EmailFilter())
async def courier_email(message: Message,state: FSMContext):
    await state.update_data(email = message.text)
    await state.set_state(CourierState.city)
    cities = []
    for i in city_info:
        if i["Город"]!="":
            cities.append(i["Город"])
        else:
            break
    await state.update_data(city = cities)
    await state.update_data(n = 1)
    builder = await create_choose_city_buttons(state)
    await message.answer("Выберите город в котором вы будете доставлять заказы. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())    

@router.message(CourierState.email)
async def email_incorrectly(message: Message):
    await message.answer(
        text="Вы написали некорректной email, повторите попытку.",
    )
    
    
#===================================Колбек кнопок городов===================================
@router.callback_query(F.data.startswith("city_"),CourierState.city)
async def customer_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    if action == "next":
        data = await state.get_data()
        n = data["n"]
        city = data['city']
        if n+1>math.ceil(len(city)/6):
            await callback.answer("Это конец списка")
            return
        else:
            n+=1
        await state.update_data(n = n)
        builder = await create_choose_city_buttons(state)
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    elif action == "back":
        data = await state.get_data()
        n = data["n"]
        city = data['city']
        if n-1<1:
            await callback.answer("Это начало списка")
            return
        else:
            n-=1
        await state.update_data(n = n)
        builder = await create_choose_city_buttons(state)
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    elif action == "break":
        await state.clear()
        await callback.message.delete()
        await callback.answer()
    else:
        await state.update_data(city = int(action))
        await state.set_state(CourierState.phone)
        builder = create_contact_button()
        await callback.message.answer("Отправьте ваш номер телефона",reply_markup=builder.as_markup(resize_keyboard=True))
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()
#===================================Город===================================
# @router.message(CourierState.city)
# async def courier_city(message: Message,state: FSMContext):
#     await state.update_data(city = message.text)
#     await state.set_state(CourierState.phone)
#     builder = create_contact_button()
#     await message.answer("Отправьте ваш номер телефона",reply_markup=builder.as_markup(resize_keyboard=True))



#===================================Номер и завершение регистрации===================================
@router.message(CourierState.phone,(F.contact!=None and F.contact.user_id == F.from_user.id))
async def courier_contact(message:Message,state: FSMContext,bot:Bot):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await state.clear()
    expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
    chat_id = city_info[data["city"]]["chat id"]
    link = await bot.create_chat_invite_link(chat_id=chat_id, expire_date= int( expire_date.timestamp()),member_limit= 1)
    msg = await message.answer(f"Регистрация успешно завершена. Вы получили 14д пробного использования.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nВ стартовом меню в разделе 'Курьер' вы можете продлить подписку.\n➖➖➖➖➖➖➖➖➖➖➖➖➖Ссылка на вступление в группу города: {link.invite_link}",reply_markup=ReplyKeyboardRemove())
    new_courier = {
        "username" : message.from_user.first_name,
        "user_id":message.from_user.id,
        "status_payment":True,
        "date_payment_expiration":str(date.today()+datetime.timedelta(days=14)),
        "date_registration":str(date.today()),
        "fio":data["fio"],
        "city":city_info[data["city"]]["Город"],
        "phone":data["phone"],
        "email":data["email"],
        "notification_one":False,
        "notification_zero":False
    }
    await database.set_courier(new_courier)


#===================================Задать вопрос===================================
class Question(StatesGroup):
    SetQuestion = State()


@router.callback_query(F.data.startswith("request-chat"))
async def request_chat(call: CallbackQuery, state: FSMContext, bot: Bot, dispatcher: Dispatcher):
    data = await database.get_request(int(call.data.split("_")[-1]))
    check = await database.check_courier(call.from_user.id)
    if not check:
        await call.answer("Вы не зарегистрированы в боте как курьер!")
    elif data["user_id_customer"] == call.from_user.id:
        await call.answer("Вы не можете задать вопрос себе!")
    else:
        await call.answer("Для продолжения перейдите в личный чат с ботом")
        msg = await bot.send_message(call.from_user.id, "Напишите свой вопрос заказчику",
                               reply_markup=custom_btn("Отмена", "start"))
        data["del"] = msg.message_id
        fsm_storage_key = StorageKey(bot_id=bot.id, user_id=call.from_user.id, chat_id=call.from_user.id)
        await dispatcher.storage.set_state(fsm_storage_key, Question.SetQuestion)
        await dispatcher.storage.update_data(fsm_storage_key, data)
        await state.update_data({"data_record": data})


@router.message(Question.SetQuestion)
async def request_chat(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data["del"], reply_markup=None)
    except:
        pass
    if not check_test(mess.text):
        await state.update_data({"text": mess.text})
        await mess.answer("Проверьте свой вопрос перед отправкой:\n\n"
                          f"{mess.text}", reply_markup=confirmation(canc_data="start"))
    else:
        msg = await mess.answer("Сообщение содержит запрещенную информацию! Уберите все ссылки и номера телефонов!")
        await state.update_data({"del": msg.message_id})

@router.callback_query(F.data.startswith("yes"), Question.SetQuestion)
async def request_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
    data_state = await state.get_data()
    await bot.send_message(data_state["user_id_customer"], f"Вопрос от курьера:\n\n{data_state['text']}",
                           reply_markup=custom_btn("Ответить", f"answer_{call.from_user.id}"))
    await call.message.edit_text("Сообщение отправлено!")
    await state.clear()

#===================================Цикл уведомлений===================================
async def check_date():
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    check_city()
    users = await database.get_notification_one(str(date.today() + datetime.timedelta(days=1)))
    for user in users:
        try:
            await bot.send_message(chat_id=user["user_id"], text="Через 1д. у вас закончится подписка курьера.")
        except TelegramBadRequest:
            pass
        finally:
            await database.change_notification_one(user["user_id"], True)
    users = await database.get_notification_zero(str(date.today()))
    for user in users:
        try:
            await bot.send_message(chat_id=user["user_id"], text="У вас закончилась подписка курьера.")
        except TelegramBadRequest:
            pass
        finally:
            await database.change_notification_zero(user["user_id"], True)
    
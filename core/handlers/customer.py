import math
import random
import datetime
import asyncio
from datetime import date
from geopy.geocoders import Nominatim

from aiogram import Router, types,F,Bot
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import StatesGroup, State

from core.settings import city_info,settings
from core.keyboards.reply import *
from core.filters.Filters import *
from core.database import database
from core.keyboards.inline import *
from core.statistics.basic import set_city_stat
from core.handlers.basic import start_call_handler
from core.message.text import get_text_start_mess, get_bet

router = Router()
#group_id = -1002057238567
group_id = -4168135619
geolocator = Nominatim(user_agent="Flow_Work.bot")


class CustomerRegistration(StatesGroup):
    fio = State()
    organization = State()
    city = State()
    email = State()
    phone = State()
    n=()

class NewForm(StatesGroup):
    city = State()
    store_name = State()
    adress_a = State()
    adress_b = State()
    cash = State()
    n = ()
    last_msg = ()
class Location(StatesGroup):
    request_info = State()
    location = State()
    translation = State()
    message = State()
    chat_id = State()
    message_to_chat =()
    customer_message_id= ()

class ChatState(StatesGroup):
    message=State()
    info = State()

# @router.message(Command(commands=["testmenu"]))
# async def testmenu(message:Message):
#     text = ""
#     text+="╭ 👤 <b>Профиль заказчика:</b>\n"
#     text+="├  📄 <b>Завершенных заявок: </b>0\n"
#     text+="╰ 📝 <b>Активных заявок: </b>0\n"
#     text+="➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
#     text+="╭ ✏️ <b>ФИО:</b> Кулаков Дмитрий Николаевич\n"
#     text+="├  💼 <b>Организация: </b>NIL\n"
#     text+="╰ 🏙️ <b>Город: </b>Новосибирск\n"
#     text+="➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
#     text+="🕒 Регистрация: 2023-03-17"
#
#     await message.answer(text)



#===================================Меню Заказчика===================================
@router.callback_query(F.data=="customer")
async def customer_callback(callback: types.CallbackQuery,bot:Bot):
    if await database.check_customer(user_id = callback.from_user.id):
        builder = create_customer_buttons(True)
        message = f"Меню заказчиков.\nЗдесь вы можете просмотреть свои заявки или создать новую."
    else:
        message = "Меню заказчиков.\nПройдите регистрацию для получения доступа к созданию заявок"
        builder = create_customer_buttons(False)
    await callback.message.edit_text(text= message,reply_markup=builder.as_markup())
    
    
    
#===================================Колбек Меню Заказчика===================================
@router.callback_query(F.data.startswith("customer_"))
async def customer_button_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    await callback.message.edit_reply_markup(reply_markup=None)
    if action == "registration":
        await state.set_state(CustomerRegistration.fio)
        await callback.message.edit_text("Введите ваше ФИО",reply_markup=None)
        await callback.answer()
    elif action == "newform":
        await state.set_state(NewForm.city)
        cities = []
        for i in city_info:
            if i["Город"] != "":
                cities.append(i["Город"])
            else:
                break
        await state.update_data(city=cities)
        await state.update_data(n = 1)
        builder = await create_choose_city_buttons(state)
        await callback.message.edit_text("Выберите город из которого бутет произведена доставка. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())
        await callback.answer()
    elif action=="forms":
        # await callback.message.delete()
        forms = await database.get_customer_sent_request(callback.from_user.id)
        for form in forms:
            if form["status_work"]=="work":
                msg = "<b>Заявка в работе</b>\n"+"-"*30+"\n"
                msg+=f"Магазин: {form['store_name']}\n"
                msg+=f"Адрес А: {form['adress_a']}\n"
                msg+=f"Адрес Б: {form['adress_b']}\n"
                msg+=f"Стоимость: {form['price']}\n"
                msg+=f"Код: {form['code']}\n"
                builder = customer_finish(form["id"])
                await callback.message.answer(text = msg,reply_markup=builder.as_markup())
            elif form["status_work"]=="sent":
                msg = "<b>Заявка отправлена</b>\n"+"-"*30+"\n"
                msg+=f"Магазин: {form['store_name']}\n"
                msg+=f"Адрес А: {form['adress_a']}\n"
                msg+=f"Адрес Б: {form['adress_b']}\n"
                msg+=f"Стоимость: {form['price']}\n"
                msg+=f"Код: {form['code']}\n"
                builder = form_cancel_chat(form["id"],form["code"])
                await callback.message.answer(text = msg,reply_markup=builder.as_markup())
        await callback.answer()


        
        
#===================================ФИО===================================
@router.message(CustomerRegistration.fio, FioFilter())
async def customer_fio(message: Message,state: FSMContext):
    await state.update_data(fio = message.text)
    await message.answer("Введите название вашей организации")
    await state.set_state(CustomerRegistration.organization)

@router.message(CustomerRegistration.fio)
async def fio_incorrectly(message: Message):
    await message.answer(
        text="Вы написали некорректное ФИО, повторите попытку.",
    )
    


#===================================Организация===================================
@router.message(CustomerRegistration.organization)
async def customer_organization(message: Message,state: FSMContext):
    await state.update_data(organization = message.text)
    await message.answer("Введите вашу почту")
    await state.set_state(CustomerRegistration.email)



#===================================Email===================================
@router.message(CustomerRegistration.email,EmailFilter())
async def customer_email(message: Message,state: FSMContext):
    await state.update_data(email = message.text)
    await state.set_state(CustomerRegistration.city)
    cities = []
    for i in city_info:
        if i["Город"]!="":
            cities.append(i["Город"])
        else:
            break
    await state.update_data({"city": cities, "n": 1})
    builder = await create_choose_city_buttons(state)
    await message.answer("Выберите ваш город. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())

@router.message(CustomerRegistration.email)
async def email_incorrectly(message: Message):
    await message.answer(
        text="Вы написали некорректной email, повторите попытку.",
    )

#===================================Колбек кнопок городов===================================
@router.callback_query(F.data.startswith("city_"),CustomerRegistration.city)
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
        await state.set_state(CustomerRegistration.phone)
        builder = create_contact_button()
        await callback.message.answer("Отправьте ваш номер телефона",reply_markup=builder.as_markup(resize_keyboard=True))
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()


# #===================================Город===================================
# @router.message(CustomerRegistration.city)
# async def customer_city(message: Message,state: FSMContext):
#     await state.update_data(city = message.text)
#     builder = create_contact_button()
#     await message.answer("Отправьте ваш номер телефона",reply_markup=builder.as_markup(resize_keyboard=True))
#     await state.set_state(CustomerRegistration.phone)


#===================================Номер и завершение регистрации===================================
@router.message(CustomerRegistration.phone,(F.contact!=None and F.contact.user_id == F.from_user.id))
async def customer_contact(message:Message,state: FSMContext,bot:Bot):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await state.clear()
    msg = await message.answer("ㅤ",reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    link = city_info[data["city"]]["ссылка"]
    builder = create_newform_button(link)
    await message.answer(text=f"Регистрация успешно завершена. Теперь вы можете создавать и просматривать свои заявки в стартовом меню или по кнопкам ниже.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nЧтобы вступить в группу города нажмите соответствующую кнопку.",reply_markup= builder.as_markup())
    new_customer = {
        "username": message.from_user.username,
        "user_id":message.from_user.id,
        "date_registration":str(date.today()),
        "fio":data["fio"],
        "city":city_info[data["city"]]["Город"],
        "phone":data["phone"],
        "email":data["email"],
        "organization":data["organization"]
    }
    await database.set_customer(new_customer)



#===================================Колбек кнопок городов в заявке===================================
@router.callback_query(F.data.startswith("city_"),NewForm.city)
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
        await callback.answer("Вы отменили заполнение заявки.")
    else:
        await state.set_state(NewForm.store_name)
        await state.update_data(city = int(action))
        builder = create_none_store_button()
        msg = await callback.message.edit_text("Введите название магазина из которого будет производиться доставка.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nЕсли доставка не из магазина, то нажмите соотвествующую кнопку.",reply_markup=builder.as_markup())
        await state.update_data(last_msg = msg.message_id)
        await callback.answer()



#===================================Магазин===================================
@router.message(NewForm.store_name)
async def form_store(message: Message,state: FSMContext):
    await state.update_data(store_name = message.text)
    builder = cancel_form_button()
    msg = await message.answer("Укажите адрес точки (через отправку геолокации), из которой будет произведена доставка (Пункт А).",reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)
    await state.set_state(NewForm.adress_a)
@router.callback_query(F.data == "none_store",NewForm.store_name)
async def form_none_store(callback: CallbackQuery,state: FSMContext):
    await state.update_data(store_name="Не из магазина.")
    builder = cancel_form_button()
    msg = await callback.message.edit_text("Укажите адрес точки (через отправку геолокации) из которой будет произведена доставка (Пункт А)",reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)
    await state.set_state(NewForm.adress_a)


#===================================Адрес-А===================================
@router.message(NewForm.adress_a, F.location!=None)
async def form_adress_a(message: Message,state: FSMContext,bot:Bot):
    coordinate = f"{message.location.latitude},{message.location.longitude}"
    await state.update_data(adress_a =  coordinate)
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id,message_id=data["last_msg"],reply_markup=None)
    builder = cancel_form_button()
    msg = await message.answer("Укажите адрес точки в которую будет произведена доставка (Пункт Б)",reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)
    await state.set_state(NewForm.adress_b)

@router.message(NewForm.adress_a, F.location==None)
async def form_adress_a_incorrectly(message: Message,state: FSMContext,bot:Bot):
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_msg"], reply_markup=None)
    builder = cancel_form_button()
    msg = await message.answer("Ошибка! Вы отправили сообщение без геолокации. "
                               "в\nПовторите попытку.",
                               reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)

#===================================Адрес-Б===================================
@router.message(NewForm.adress_b, F.location!=None)
async def form_adress_b(message: Message,state: FSMContext,bot:Bot):
    coordinate = f"{message.location.latitude},{message.location.longitude}"
    await state.update_data(adress_b=coordinate)
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_msg"], reply_markup=None)
    builder = cancel_form_button()
    msg = await message.answer(f"Укажите стоимость доставки (минимальное значение {get_bet()})",
                               reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)
    await state.set_state(NewForm.cash)

@router.message(NewForm.adress_b, F.location==None)
async def form_adress_a_incorrectly(message: Message,state: FSMContext,bot:Bot):
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_msg"], reply_markup=None)
    builder = cancel_form_button()
    msg = await message.answer("Ошибка! Вы отправили сообщение без геолокации.\nПовторите попытку.",
                               reply_markup=builder.as_markup())
    await state.update_data(last_msg=msg.message_id)

#===================================Стоимость===================================
@router.message(NewForm.cash)
async def form_store(message: Message,state: FSMContext,bot:Bot):
    builder = cancel_form_button()
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_msg"], reply_markup=None)
    try:
        if int(message.text)<get_bet():
            msg = await message.answer(f"Минимально возможная стоимость на данный момент: {get_bet()}!", reply_markup=builder.as_markup())
            await state.update_data(last_msg=msg.message_id)
            return
    except ValueError:
        msg = await message.answer("Введенные данные не являются числом!", reply_markup=builder.as_markup())
        await state.update_data(last_msg=msg.message_id)
        return
    await state.update_data(cash = message.text)
    data["cash"] = message.text
    msg = "Верны ли введенные данные?"
    msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    city = city_info[data["city"]]["Город"]
    msg+=f"Город: {city}\n"
    msg+=f"Магазин: {data['store_name']}\n"
    adress_a = ", ".join(geolocator.reverse(data['adress_a']).address.split(", ")[:4])
    adress_b = ", ".join(geolocator.reverse(data['adress_b']).address.split(", ")[:4])
    msg+=f"Адрес А:  <code>{adress_a}</code>\n"
    msg+=f"Адрес Б:  <code>{adress_b}</code>\n"
    msg+=f"Стоимость доставки: {data['cash']}\n"
    builder = create_customer_send_form_buttons()
    await message.answer(msg,reply_markup=builder.as_markup())



#===================================Колбек кнопок валидности данных===================================
@router.callback_query(F.data.startswith("form_"))
async def customer_form_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    if action == "send":
        data = await state.get_data()
        alphabet = list("abcdefghijklmnopqrstuvwxyz")
        upp = list("abcdefghijklmnopqrstuvwxyz".upper())
        code_array = alphabet+upp+list("1234567890")
        code=""
        for i in range(5):
            code+=random.choice(code_array)
        await callback.message.delete()
        chat_id = city_info[data["city"]]["chat id"]
        await callback.message.answer("Заявка отправлена в группу города.")
        await callback.answer()
        msg = "<b>ЗАЯВКА</b>"
        msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        data = await state.get_data()
        msg+=f"Магазин: {data['store_name']}\n"
        city = city_info[data["city"]]["Город"]
        msg+=f"Город: {city}\n"
        adress_a = ", ".join(geolocator.reverse(data['adress_a']).address.split(", ")[:4])
        adress_b = ", ".join(geolocator.reverse(data['adress_b']).address.split(", ")[:4])
        msg += f"Адрес А:  <code>{adress_a}</code>\n"
        msg += f"Адрес А:  <code>{adress_b}</code>\n"
        msg+=f"Стоимость: {data['cash']}\n"
        msg = await bot.send_message(chat_id = chat_id, text = msg)
        newreq = {
            "username_customer":callback.from_user.username,
            "user_id_customer":callback.from_user.id,
            "date_registration":str(date.today()),
            "status_work":"sent",
            "adress_a":data["adress_a"],
            "adress_b":data["adress_b"],
            "code":code,
            "price":int(data["cash"]),
            "store_name":data["store_name"],
            "message_id":msg.message_id,
            "chat_id":chat_id
        }
        await database.set_request(newreq)
        builder = create_form_buttons(await database.get_request_id(msg.message_id))
        await bot.edit_message_reply_markup(chat_id=chat_id,message_id=msg.message_id,reply_markup=builder.as_markup())
        await state.clear()
        await callback.answer()
        set_city_stat("record_new", chat_id)
    elif action == "repeat":
        await callback.message.delete()
        await state.set_state(NewForm.city)
        cities = []
        for i in city_info:
            if i["Город"] != "":
                cities.append(i["Город"])
            else:
                break
        await state.update_data(city=cities)
        await state.update_data(n = 1)
        builder = await create_choose_city_buttons(state)
        await callback.message.answer("Выберите город из которого бутет произведена доставка. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())
        await callback.answer()
    else:
        await callback.message.delete()
        await state.clear()
        await callback.answer()

#===================================Кнопка отмены===================================
@router.callback_query(F.data == "cancel_form")
async def cancel_form(callback: types.CallbackQuery,state:FSMContext):
    await state.clear()
    await start_call_handler(callback,state)

#===================================Колбек кнопок на заявке===================================
@router.callback_query(F.data.startswith("request_"))
async def customer_forms_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    if not(await database.check_courier(user_id = callback.from_user.id)):
        await callback.answer(f"Вы не зарегистрированны как курьер. Пройдите регистрацию в нашем боте.")
        return
    courier = await database.get_courier(user_id = callback.from_user.id)
    if courier["status_payment"]==False or courier["verification"]==False:
        await callback.answer(f"Вы не верифицированы или у вас закончилась подписка курьера.")
        return
    action = callback.data.split("_")[1]
    if action == "chat":
        pass
    else:
        form = await database.get_request(int(action))
        # if form["user_id_customer"]==callback.from_user.id:
        #     await callback.answer("Вы не можете отвечать на свою заявку.")
        #     return
        msg = "<b>На вашу заявку ответили</b>\n"+"➖➖➖➖➖➖➖➖➖➖➖➖➖"+"\n"
        msg+="Информация о курьере:\n"
        msg+=f"ФИО: {courier['fio']}\n"
        msg+=f"Номер телефона: {courier['phone']}\n"
        msg += f"Количество оценок: {courier['n_score']}\n"
        if courier['n_score']>0:
            msg += f"Средний рейтинг: {courier['score']/round(courier['n_score'],2)}\n"
        else:
            msg += f"Средний рейтинг: 0\n"
        msg+="➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        msg+=f"Магазин: {form['store_name']}\n"
        adress_a = ", ".join(geolocator.reverse(form['adress_a']).address.split(", ")[:4])
        adress_b = ", ".join(geolocator.reverse(form['adress_b']).address.split(", ")[:4])
        msg += f"Адрес А:  <code>{adress_a}</code>\n"
        msg += f"Адрес Б:  <code>{adress_b}</code>\n"
        msg+=f"Стоимость: {form['price']}\n"
        msg+=f"Код: {form['code']}\n"
        builder = status_work()
        await bot.edit_message_reply_markup(chat_id=form["chat_id"],message_id=form["message_id"],reply_markup=builder.as_markup())
        customer_message = await bot.send_message(chat_id = form["user_id_customer"], text = msg,reply_markup=form_cancel_chat(int(action),callback.from_user.id,form["code"]))
        msg = "<b>Вы ответили на заявку</b>"
        msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        msg+=f"Магазин: {form['store_name']}\n"
        msg += f"Адрес А:  <code>{adress_a}</code>\n"
        msg += f"Адрес Б:  <code>{adress_b}</code>\n"
        msg+=f"Стоимость: {form['price']}\n"
        msg+=f"Код: {form['code']}\n"
        msg = await bot.send_message(chat_id = callback.from_user.id, text = msg,reply_markup=courier_start_finish(int(action),customer_message.message_id,form["user_id_customer"],form["code"]))
        await database.change_status_work(int(action),"call")
        await database.set_request_courier(int(action),callback.from_user.id, msg.message_id)

@router.callback_query(StartFinishCourier.filter(F.action=="start"))
async def callbacks_start_courier(
        callback: types.CallbackQuery,
        callback_data: StartFinishCourier,
        bot:Bot, state:FSMContext
):
    form = await database.get_request(callback_data.request_id)
    form["id"]=callback_data.request_id
    await bot.edit_message_reply_markup(chat_id=form["user_id_customer"], message_id=callback_data.customer_message_id,
                                        reply_markup=start_chat_button(callback.from_user.id,form["code"]))
    await state.set_state(Location.location)
    await state.update_data({"request_info": form,"customer_message_id":callback_data.customer_message_id})
    await database.change_status_work(callback_data.request_id, "work")
    await callback.message.answer("Отправьте свое местоположение с трансляцией для отображения ее заказчику")
    await callback.message.delete()
    await callback.answer()

@router.callback_query(StartFinishCourier.filter(F.action=="finish"))
async def callbacks_cancel_courier(
        callback: types.CallbackQuery,
        callback_data: StartFinishCourier,
        bot:Bot
):

    form = await database.get_request(callback_data.request_id)
    if form["status_work"] == "finish" or form["status_work"] == "sent":
        await callback.answer("Нельзя отменить эту заявку.")
        return
    await database.change_status_work(callback_data.request_id, "sent")
    await callback.message.delete()
    await bot.send_message(chat_id=form["user_id_customer"],
                           text=f"Курьер отказался от заявки с кодом <b>{form['code']}</b>.\nЗаявка снова открыта.")
    await bot.delete_message(chat_id=form["user_id_customer"],message_id=callback_data.customer_message_id)
    builder = create_form_buttons(await database.get_request_id(form["message_id"]))
    await bot.edit_message_reply_markup(chat_id=form["chat_id"], message_id=form["message_id"],
                                        reply_markup=builder.as_markup())
    await callback.answer("Вы отменили заявку.")


#===================================Отмена заявки в меню кастомера===================================
@router.callback_query(F.data.startswith("formcancel_"))
async def customer_forms_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    form = await database.get_request(int(action))
    await database.change_status_work(int(action),"finish")
    try:
        await callback.message.delete()
        await bot.delete_message(chat_id=form["chat_id"],message_id=form["message_id"])
        if (form["message_courier_id"]):
            await bot.delete_message(chat_id=form["courier_id"], message_id=form["message_courier_id"])
            await bot.send_message(chat_id=form["courier_id"], text=f"Заказчик отменил заявку с кодом {form['code']}. Сообщение было удалено.")
    except:
        pass
    finally:
        await callback.answer("Заявка отменена.")

        set_city_stat("record_cancel", form["chat_id"])

#===================================Колбек на принятие товара===================================
# @router.callback_query(F.data.startswith("start_courier_"))
# async def customer_forms_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
#     action = callback.data.split("_")[2]
#     form = await database.get_request(int(action))
#     await bot.edit_message_reply_markup(chat_id=form["user_id_customer"],message_id=form["message_id"],reply_markup=None)
#     await state.set_state(Location.location)
#     await state.update_data({"request_info":form})
#     await database.change_status_work(int(action),"work")
#     await callback.message.answer("Отправьте свое местоположение с трансляцией для отображения ее заказчику")
#     await callback.message.delete()
#     await callback.answer()

#===================================Обработка отправки геопозиции для трансляции===================================
@router.message(Location.location, (F.location!=None and F.location.live_period!=None))
async def courier_location(message: Message, state: FSMContext,bot:Bot) -> None:
    await state.update_data(location=message.location)
    await state.update_data(translation=message)
    data = await state.get_data()
    msg = await bot.send_location(chat_id=data["request_info"]["user_id_customer"], latitude=data["location"].latitude, longitude=data["location"].longitude, live_period=message.location.live_period)
    await state.update_data({"message_id":msg.message_id,"chat_id":msg.chat.id})
    form = data["request_info"]
    msg = "<b>Текущая заявка</b>"
    msg+="\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    msg += f"Магазин: {form['store_name']}\n"
    adress_a = ", ".join(geolocator.reverse(form['adress_a']).address.split(", ")[:4])
    adress_b = ", ".join(geolocator.reverse(form['adress_b']).address.split(", ")[:4])
    msg += f"Адрес А:  <code>{adress_a}</code>\n"
    msg += f"Адрес Б:  <code>{adress_b}</code>\n"
    msg += f"Стоимость: {form['price']}\n"
    msg += f"Код: {form['code']}\n"
    href = f"maps.yandex.ru/?rtext={form['adress_a']}~{form['adress_b']}&rtt=mt"
    msg += f'Ссылка на маршрут: <a href = "{href}">Маршрут</a>\n'
    await message.answer(text = msg,reply_markup=translatelocation_buttons(form['user_id_customer'],form["code"]),parse_mode="HTML")
    await state.set_state(Location.translation)
@router.message(Location.location, F.location!=None)
async def courier_location_uncorrectly_callback(message: Message):
    await message.answer("Некорректная геопозиция. Отправьте повторно с трансляцией вашего местоположения.")


@router.edited_message(Location)
async def edited_message_handler(edited_message: types.Message,state: FSMContext,bot:Bot) -> None:
    data = await state.get_data()
    if edited_message.location!=None:
        if edited_message.location.live_period!=None:
            await bot.edit_message_live_location(chat_id=data["chat_id"],message_id=data["message_id"],
                                             latitude=edited_message.location.latitude,
                                             longitude=edited_message.location.longitude)


@router.callback_query(Location.translation, F.data == "finishrequest")
async def finishrequest(callback:CallbackQuery,state:FSMContext,bot:Bot):
    data = await state.get_data()
    await state.clear()
    await bot.delete_message(chat_id=data["chat_id"],message_id=data["message_id"])
    await bot.delete_message(chat_id=data["translation"].chat.id,message_id=data["translation"].message_id)
    await bot.delete_message(chat_id=data["request_info"]["chat_id"],message_id=data["request_info"]["message_id"])
    await bot.delete_message(chat_id=data["request_info"]["user_id_customer"],message_id=data["customer_message_id"])
    await bot.send_message(chat_id=data["request_info"]["user_id_customer"],text=f"Курьер завершил доставку по заявке с кодом {data['request_info']['code']}.\nНе забудьте об оплате, а также по желанию оцените курьера с помощью кнопок ниже.",reply_markup=add_score_button(data['request_info']['courier_id'],data['request_info']['id']))
    await callback.message.answer(f"Вы завершили доставку по заявке с кодом {data['request_info']['code']}.\nОжидайте поступления перевода.")
    await callback.message.delete()

    await callback.answer()

@router.callback_query(AddScore.filter())
async def add_score(callback: types.CallbackQuery,callback_data: AddScore,state:FSMContext):
    if callback_data.score!=0:
        await database.add_score_courier(callback_data.courier_id,callback_data.score)
        await callback.answer("Благодарим за оценку")
    await database.change_status_work(callback_data.request_id, "finish")
    await start_call_handler(callback,state)

#===================================Колбек кнопок на заявке в работе===================================
@router.callback_query(F.data.startswith("finish_"))
async def all_form_button_callback(callback: types.CallbackQuery,bot: Bot):
    autor = callback.data.split("_")[1]
    id = callback.data.split("_")[2]
    if autor=="customer":
        await database.change_status_work(int(id),"finish")
        form = await database.get_request(int(id))
        try:
            await bot.delete_message(chat_id=form["chat_id"],message_id=form["message_id"])
            await callback.message.delete()
        except:
            pass
        finally:
            await callback.answer("Заявка завершена.")
            set_city_stat("record_done", callback.message.chat.id)
    # else:
    #     form = await database.get_request(int(id))
    #     if form["status_work"]=="finish" or form["status_work"]=="sent":
    #         await callback.answer("Нельзя отменить эту заявку.")
    #         return
    #     await database.change_status_work(int(id),"sent")
    #     await callback.message.delete()
    #
    #     await bot.send_message(chat_id=form["user_id_customer"],text=f"Курьер отказался от заявки с кодом <b>{form['code']}</b>.\nЗаявка снова открыта.")
    #     builder = create_form_buttons(await database.get_request_id(form["message_id"]))
    #     await bot.edit_message_reply_markup(chat_id=form["chat_id"], message_id=form["message_id"],
    #                                         reply_markup=builder.as_markup())
    #     await callback.answer("Вы отменили заявку.")


#===================================Ответить на вопрос===================================
class Answer(StatesGroup):
    SetAnswer = State()


@router.callback_query(F.data.startswith("answer"))
async def request_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
    msg = await bot.send_message(call.from_user.id, "Напишите свой ответ курьеру",
                           reply_markup=custom_btn("Отмена", "start"))
    await state.set_state(Answer.SetAnswer)
    await state.update_data({"courier_id": call.data.split("_")[-1], "del": msg.message_id})


@router.message(Answer.SetAnswer)
async def request_chat(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.edit_message_reply_markup(mess.chat.id, data["del"], reply_markup=None)
    except:
        pass
    if not check_test(mess.text):
        await state.update_data({"text": mess.text})
        await mess.answer("Проверьте свой ответ перед отправкой:\n\n"
                          f"{mess.text}", reply_markup=confirmation(canc_data="start"))
    else:
        msg = await mess.answer("Сообщение содержит запрещенную информацию! Уберите все ссылки и номера телефонов!")
        await state.update_data({"del": msg.message_id})


@router.callback_query(F.data.startswith("yes"), Answer.SetAnswer)
async def request_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
    data_state = await state.get_data()
    await bot.send_message(data_state["courier_id"], f"Ответ от заказчика:\n\n{data_state['text']}")
    await call.message.edit_text("Сообщение отправлено!")
    await state.clear()


@router.callback_query(Chat.filter())
async def request_chat(callback: CallbackQuery,callback_data:Chat, state:FSMContext):
    if await state.get_state():
        pass
    else:
        await callback.message.answer("Напишите ваше сообщение для отправки собеседнику")
        await state.set_state(ChatState.message)
        await state.update_data({"info":[callback_data.user_id,callback_data.code]})
        await callback.answer()
@router.message(ChatState.message)
async def send_message_chat(message: Message,state:FSMContext,bot:Bot):
    data = await state.get_data()
    msg = f"Сообщение по заявке с кодом {data['info'][1]}"
    msg+="\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    msg+=message.text

    await bot.send_message(chat_id=data["info"][0],text=msg,reply_markup=answer_chat_button(message.from_user.id,data["info"][1]))

@router.callback_query(AnswerChat.filter())
async def answer_chat(callback: CallbackQuery,callback_data:Chat,bot:Bot):
    msg = f"Сообщение по заявке с кодом {callback_data.request_code}"
    msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    msg += "Сообщение прочитано."
    await bot.send_message(chat_id=callback_data.user_id,text=msg)
    await callback.answer()
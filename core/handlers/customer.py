from aiogram import Router, types,F,Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command,CommandStart, BaseFilter
from aiogram.types import Message, ReplyKeyboardRemove
import math
import random
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.keyboards.inline import *
from core.keyboards.reply import *
from core.filters.Filters import *
from core.settings import worksheet_city
from core.handlers.courier import city_info
import datetime
from datetime import date
import database

router = Router()
#group_id = -1002057238567
group_id = -4168135619

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
class City(StatesGroup):
    city = State()
    n = ()


@router.message(Command(commands=["testmenu"]))
async def testmenu(message:Message):
    text = ""
    text+="╭ 👤 <b>Профиль заказчика:</b>\n"
    text+="├  📄 <b>Завершенных заявок: </b>0\n"
    text+="╰ 📝 <b>Активных заявок: </b>0\n"
    text+="➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    text+="╭ ✏️ <b>ФИО:</b> Кулаков Дмитрий Николаевич\n"
    text+="├  💼 <b>Организация: </b>NIL\n"
    text+="╰ 🏙️ <b>Город: </b>Новосибирск\n"
    text+="➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    text+="🕒 Регистрация: 2023-03-17"
    
    await message.answer(text)



#===================================Меню Заказчика===================================
@router.callback_query(F.data=="customer")
async def customer_callback(callback: types.CallbackQuery,bot:Bot):
    if await database.check_customer(user_id = callback.from_user.id):
        expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
        builder = create_customer_buttons(True) 
        message = f"Меню заказчиков.\nЗдесь вы можете просмотреть свои заявки или создать новую."
    else:
        message = "Меню заказчиков.\nПройдите регистрацию для получения доступа к созданию заявок"
        builder = create_customer_buttons(False)
    await callback.message.edit_text(text= message,reply_markup=builder.as_markup())
    
    
    
#===================================Колбек Меню Заказчика===================================
@router.callback_query(F.data.startswith("customer_"))
async def customer_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    if action == "registration":
        await state.set_state(CustomerRegistration.fio)
        await callback.message.answer("Введите ваше ФИО")
        await callback.answer()
    elif action == "newform":
        await state.set_state(City.city)
        cities = worksheet_city.col_values(1)[1:]
        await state.update_data(city = cities)
        await state.update_data(n = 1)
        builder = await create_choose_city_buttons(state)
        await callback.message.answer("Выберите город из которого бутет произведена доставка. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())    
        await callback.answer()
    elif action == "back":
        builder = create_start_buttons()
        await callback.message.edit_text("Приветственное сообщение", reply_markup=builder.as_markup())
    elif action=="forms":
        forms = await database.get_customer_sent_request(callback.from_user.id)
        for form in forms:
            if form["status_work"]=="work":
                msg = "<b>Заявка в работе</b>\n"+"-"*30+"\n"
                msg+=f"Магазин: {form["store_name"]}\n"
                msg+=f"Адрес А: {form["adress_a"]}\n"
                msg+=f"Адрес Б: {form["adress_b"]}\n"
                msg+=f"Стоимость: {form["price"]}\n"
                msg+=f"Код: {form["code"]}\n"
                builder = customer_finish(form["id"])
                await callback.message.answer(text = msg,reply_markup=builder.as_markup())
            elif form["status_work"]=="sent":
                msg = "<b>Заявка отправлена</b>\n"+"-"*30+"\n"
                msg+=f"Магазин: {form["store_name"]}\n"
                msg+=f"Адрес А: {form["adress_a"]}\n"
                msg+=f"Адрес Б: {form["adress_b"]}\n"
                msg+=f"Стоимость: {form["price"]}\n"
                msg+=f"Код: {form["code"]}\n"
                builder = form_cancel(form["id"])
                await callback.message.answer(text = msg,reply_markup=builder.as_markup())
        await callback.answer()
                
        
        
        
#===================================ФИО===================================
@router.message(CustomerRegistration.fio,FioFilter())
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
    await state.update_data(city = cities)
    await state.update_data(n = 1)
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
    expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
    chat_id = city_info[data["city"]]["chat id"]
    link = await bot.create_chat_invite_link(chat_id=chat_id, expire_date= int( expire_date.timestamp()),member_limit= 1)
    await message.answer(f"Регистрация успешно завершена. Теперь вы можете создавать свои заявки.\nСсылка на вступление в группу города: {link.invite_link}",reply_markup=ReplyKeyboardRemove())
    new_customer =  {
        "username" : message.from_user.username,
        "user_id":message.from_user.id,
        "date_registration":str(date.today()),
        "fio":data["fio"],
        "city":city_info[data["city"]]["Город"],
        "phone":data["phone"],
        "email":data["email"],
        "organization":data["organization"]
    }
    await database.set_customer(new_customer)



#===================================Колбек кнопок городов===================================
@router.callback_query(F.data.startswith("city_"),City.city)
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
        await state.set_state(NewForm.store_name)
        await state.update_data(city = int(action))
        builder = create_none_store_button()
        await callback.message.answer("Введите название с которого будут доставлять. Если доставка не из магазина, то нажмите соотвествующую кнопку.",reply_markup=builder.as_markup(resize_keyboard=True))
        await callback.answer()



#===================================Магазин===================================
@router.message(NewForm.store_name)
async def form_store(message: Message,state: FSMContext):
    await state.update_data(store_name = message.text)
    await message.answer("Укажите адрес точки из которой будет произведена доставка (Пункт А)",reply_markup=ReplyKeyboardRemove())
    await state.set_state(NewForm.adress_a)



#===================================Адрес-А===================================
@router.message(NewForm.adress_a)
async def form_adress_a(message: Message,state: FSMContext):
    await state.update_data(adress_a = message.text)
    await message.answer("Укажите адрес точки в которую будет произведена доставка (Пункт Б)")
    await state.set_state(NewForm.adress_b)



#===================================Адрес-Б===================================
@router.message(NewForm.adress_b)
async def form_adress_b(message: Message,state: FSMContext):
    await state.update_data(adress_b = message.text)
    await message.answer("Укажите стоимость доставки")
    await state.set_state(NewForm.cash)



#===================================Стоимость===================================
@router.message(NewForm.cash)
async def form_store(message: Message,state: FSMContext):
    await state.update_data(cash = message.text)
    msg = "Верны ли введенные данные?\n"+"-"*30+"\n"
    data = await state.get_data()
    city = worksheet_city.col_values(1)[1:][data["city"]]
    msg+=f"Город: {city}\n"
    msg+=f"Магазин: {data["store_name"]}\n"
    msg+=f"Адрес А: {data["adress_a"]}\n"
    msg+=f"Адрес Б: {data["adress_b"]}\n"
    msg+=f"Стоимость доставки: {data["cash"]}\n"
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
        msg = "<b>ЗАЯВКА</b>\n"+"-"*30+"\n"
        data = await state.get_data()
        msg+=f"Магазин: {data["store_name"]}\n"
        city = city_info[data["city"]]["Город"]
        msg+=f"Город: {city}\n"
        msg+=f"Адрес А: {data["adress_a"]}\n"
        msg+=f"Адрес Б: {data["adress_b"]}\n"
        msg+=f"Стоимость: {data["cash"]}\n"
        msg = await bot.send_message(chat_id = group_id, text = msg)
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
            "chat_id":group_id
        }
        await database.set_request(newreq)
        builder = create_form_buttons(await database.get_request_id(msg.message_id))
        await bot.edit_message_reply_markup(chat_id=group_id,message_id=msg.message_id,reply_markup=builder.as_markup())
        await state.clear()
        await callback.answer()
    elif action == "repeat":
        await callback.message.delete()
        await state.set_state(City.city)
        cities = worksheet_city.col_values(1)[1:]
        await state.update_data(city = cities)
        await state.update_data(n = 1)
        builder = await create_choose_city_buttons(state)
        await callback.message.answer("Выберите город из которого бутет произведена доставка. Если вашего города нет, то выбирайте ближайший.",reply_markup = builder.as_markup())    
        await callback.answer()
    else:
        await callback.message.delete()
        await state.clear()
        await callback.answer()
        
        
        
#===================================Колбек кнопок на заявке===================================
@router.callback_query(F.data.startswith("request_"))
async def customer_forms_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    if action == "chat":
        pass
    else:
        form = await database.get_request(int(action))
        if form["user_id_customer"]==callback.from_user.id:
            callback.message.answer("Вы не можете отвечать на свою заявку.")
            return
        msg = "<b>На вашу заявку ответили</b>\n"+"-"*30+"\n"
        msg+=f"Магазин: {form["store_name"]}\n"
        msg+=f"Адрес А: {form["adress_a"]}\n"
        msg+=f"Адрес Б: {form["adress_b"]}\n"
        msg+=f"Стоимость: {form["price"]}\n"
        msg+=f"Код: {form["code"]}\n"
        builder = status_work()
        await bot.edit_message_reply_markup(chat_id=form["chat_id"],message_id=form["message_id"],reply_markup=builder.as_markup())
        builder = customer_finish(int(action))
        await bot.send_message(chat_id = form["user_id_customer"], text = msg,reply_markup=builder.as_markup())
        msg = "<b>Вы ответили на заявку</b>\n"+"-"*30+"\n"
        msg+=f"Магазин: {form["store_name"]}\n"
        msg+=f"Адрес А: {form["adress_a"]}\n"
        msg+=f"Адрес Б: {form["adress_b"]}\n"
        msg+=f"Стоимость: {form["price"]}\n"
        msg+=f"Код: {form["code"]}\n"
        builder = courier_finish(int(action))
        await bot.send_message(chat_id = callback.from_user.id, text = msg,reply_markup=builder.as_markup())
        await database.change_status_work(int(action),"work")



#===================================Отмена заявки в меню кастомера===================================
@router.callback_query(F.data.startswith("formcancel_"))
async def customer_forms_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]
    form = await database.get_request(int(action))
    await database.change_status_work(int(action),"finish")
    try:
        await bot.delete_message(chat_id=form["chat_id"],message_id=form["message_id"])
        await callback.message.delete()
    except:
        pass
    finally:
        await callback.answer("Заявка отменена.")

#===================================Колбек кнопок на заявке в работе===================================
@router.callback_query(F.data.startswith("finish_"))
async def all_form_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
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
            await callback.answer()
    else:
        form = await database.get_request(int(id))
        if form["status_work"]=="finish":
            await callback.answer("Заявка уже завершена.")
            return
        await database.change_status_work(id,"sent")
        await bot.send_message(chat_id=form["user_id_customer"],text=f"Курьер отказался от заявки с кодом <b>{form["code"]}</b>.\nЗаявка снова открыта.")
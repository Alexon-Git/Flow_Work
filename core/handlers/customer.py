from aiogram import Router, types,F,Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command,CommandStart, BaseFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.keyboards.inline import *
from core.keyboards.reply import *
from core.filters.Filters import *
import datetime
from datetime import date
import database

router = Router()
group_id = -1002057238567

class CustomerRegistration(StatesGroup):
    fio = State()
    organization = State()
    city = State()
    email = State()
    phone = State()
    


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
        link = await bot.create_chat_invite_link(chat_id=group_id, expire_date= int( expire_date.timestamp()),member_limit= 1)
        builder = create_customer_buttons(True,link.invite_link) 
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
    elif action == "back":
        builder = create_start_buttons()
        await callback.message.edit_text("Приветственное сообщение", reply_markup=builder.as_markup())
        
        
        
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
    await message.answer("Введите ваш город")
    await state.set_state(CustomerRegistration.city)
    
@router.message(CustomerRegistration.email)
async def email_incorrectly(message: Message):
    await message.answer(
        text="Вы написали некорректной email, повторите попытку.",
    )



#===================================Город===================================
@router.message(CustomerRegistration.city)
async def customer_city(message: Message,state: FSMContext):
    await state.update_data(city = message.text)
    builder = create_contact_button()
    await message.answer("Отправьте ваш номер телефона",reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(CustomerRegistration.phone)


#===================================Номер и завершение регистрации===================================
@router.message(CustomerRegistration.phone,(F.contact!=None and F.contact.user_id == F.from_user.id))
async def customer_contact(message:Message,state: FSMContext,bot:Bot):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await state.clear()
    expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
    link = await bot.create_chat_invite_link(chat_id=group_id, expire_date= int( expire_date.timestamp()),member_limit= 1)
    await message.answer(f"Регистрация успешно завершена. Теперь вы можете создавать свои заявки.\nСсылка на вступление в группу города: {link.invite_link}",reply_markup=ReplyKeyboardRemove())
    new_customer =  {
        "username" : message.from_user.username,
        "user_id":message.from_user.id,
        "date_registration":str(date.today()),
        "fio":data["fio"],
        "city":data["city"],
        "phone":data["phone"],
        "email":data["email"],
        "organization":data["organization"]
    }
    await database.set_customer(new_customer)
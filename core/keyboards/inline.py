from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import datetime

start_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть отзыв", callback_data="courier")],
    [InlineKeyboardButton(text="Оставить отзыв", callback_data="customer")]    
])



def create_start_buttons()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Заказчик",
        callback_data=f"customer")
    )
    builder.add(InlineKeyboardButton(
        text="Курьер",
        callback_data=f"courier")
    )
    return builder

def create_courier_buttons(registration: bool,link=None)->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=f"courier_back")
    )
    if registration:
        builder.add(InlineKeyboardButton(
            text="Оплата",
            callback_data=f"courier_payment")
        )
        
        builder.row(InlineKeyboardButton(
            text="Группа города",
            url=link)
        )        
    else:        
        builder.add(InlineKeyboardButton(
            text="Регистрация",
            callback_data=f"courier_registration")
        ) 
    return builder

def create_customer_buttons(registration: bool)->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=f"customer_back")
    )
    if registration:
        builder.add(InlineKeyboardButton(
            text="Мои заявки",
            callback_data=f"customer_forms")
        )
        builder.row(InlineKeyboardButton(
            text="Новая заявка",
            callback_data="customer_newform")
        )      
    else:        
        builder.add(InlineKeyboardButton(
            text="Регистрация",
            callback_data=f"customer_registration")
        ) 
    return builder

def create_customer_send_form_buttons()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Да",
        callback_data="form_send"
    ))
    builder.add(InlineKeyboardButton(
        text="Нет",
        callback_data="form_repeat"
    ))
    builder.row(InlineKeyboardButton(
        text="Отмена",
        callback_data="form_break"
    ))
    return builder 

async def create_choose_city_buttons(state:FSMContext)->InlineKeyboardBuilder:
    data = await state.get_data()
    n = data["n"]
    n-=1
    n*=6
    city = data["city"]
    builder = InlineKeyboardBuilder()
    for i in range(6):
        if n+i <= len(city)-1:
            button = InlineKeyboardButton(
                text=city[n+i],
                callback_data=f"city_{n+i}")
        else:
            button = InlineKeyboardButton(
                text="➖",
                callback_data=f"none")
        if (n+i)%3 == 0 or (n+i)%3==3:
            builder.row(button)
        else:
            builder.add(button)
    builder.row(InlineKeyboardButton(
        text="<--",
        callback_data=f"city_back")
    )
    builder.add(InlineKeyboardButton(
        text="Отмена",
        callback_data=f"city_break")
    )
    builder.add(InlineKeyboardButton(
        text="-->",
        callback_data=f"city_next")
    )   
    return builder
  
def status_work()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="В работе",
        callback_data="none"
    ))
    return builder
 
def form_cancel(id:int)->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Отменить заявку",
        callback_data=f"formcancel_{id}"
    ))
    return builder
          
def customer_finish(id:int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Завершить",
        callback_data=f"finish_customer_{id}"
    ))
    return builder

def courier_finish(id:int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Отмена",
        callback_data=f"finish_courier_{id}"
    ))
    return builder
  
def create_form_buttons(id:int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Откликнуться",
        callback_data=f"request_{id}"
    ))
    builder.row(InlineKeyboardButton(
        text="Задать вопрос",
        callback_data="request_chat"
    ))
    return builder
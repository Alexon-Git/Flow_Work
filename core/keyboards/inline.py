from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

def create_customer_buttons(registration: bool,link=None)->InlineKeyboardBuilder:
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
        builder.row(InlineKeyboardButton(
            text="Группа",
            url=link)
        )        
    else:        
        builder.add(InlineKeyboardButton(
            text="Регистрация",
            callback_data=f"customer_registration")
        ) 
    return builder
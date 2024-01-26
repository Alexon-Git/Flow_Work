from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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

def create_courier_buttons(registration: bool)->InlineKeyboardBuilder:
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
    else:        
        builder.add(InlineKeyboardButton(
            text="Регистрация",
            callback_data=f"courier_reg")
        )
    return builder
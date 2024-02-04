from core.google_doc.googleSheets import get_id_admin
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть отзыв", callback_data="courier")],
    [InlineKeyboardButton(text="Оставить отзыв", callback_data="customer")]    
])


def create_start_buttons(user_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Заказчик",
        callback_data="customer")
    )
    builder.add(InlineKeyboardButton(
        text="Курьер",
        callback_data="courier")
    )
    if user_id in get_id_admin():
        builder.add(InlineKeyboardButton(text='Администратору', callback_data="admin"))
    return builder


def create_courier_buttons(registration: bool, link=None) -> InlineKeyboardBuilder:
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


def create_customer_buttons(registration: bool, link=None) -> InlineKeyboardBuilder:
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


def admin_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Рассылка сообщений по пользователям", callback_data="notif")],
        [InlineKeyboardButton(text="Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="Просмотр Заказчиков", callback_data="view_customer")],
        [InlineKeyboardButton(text="Просмотр Курьеров", callback_data="view_courier")],
        [InlineKeyboardButton(text="Изменить стоимость подписки", callback_data="edit_amount")],
        [InlineKeyboardButton(text="В меню", callback_data="menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "Да", txt_n: str = "Нет"):
    buttons = [
        [InlineKeyboardButton(text=txt_y, callback_data="yes")],
        [InlineKeyboardButton(text=txt_n, callback_data="no")],
        [InlineKeyboardButton(text="Отмена", callback_data="start")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def choice_people():
    buttons = [
        [InlineKeyboardButton(text="Курьеры", callback_data="notif_courier")],
        [InlineKeyboardButton(text="Заказчики", callback_data="notif_customer")],
        [InlineKeyboardButton(text="Все", callback_data="notif_all")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="start")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

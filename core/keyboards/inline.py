from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from core.settings import settings
from core.database.database import get_id_admin


async def create_start_buttons(user_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Заказчик",
        callback_data="customer")
    )
    builder.add(InlineKeyboardButton(
        text="Курьер",
        callback_data="courier")
    )
    if user_id in (await get_id_admin()):
        builder.row(InlineKeyboardButton(text='Администратору', callback_data="admin"))
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


def create_customer_buttons(registration: bool) -> InlineKeyboardBuilder:
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

def create_newform_button()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Новая заявка",
        callback_data="customer_newform")
    )
    builder.add(InlineKeyboardButton(
        text="Мои заявки",
        callback_data=f"customer_forms")
    )
    return builder

def create_customer_send_form_buttons() -> InlineKeyboardBuilder:
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


def admin_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Рассылка сообщений по пользователям", callback_data="notif")],
        [InlineKeyboardButton(text="Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="Изменить стоимость подписки", callback_data="edit_amount")],
        [InlineKeyboardButton(text="Просмотр Заказчиков/Курьеров", callback_data="view_record")],
    ]
    if user_id == settings.bots.admin_id:
        buttons.append([InlineKeyboardButton(text="Добавить администратора", callback_data="add_admin")])
        buttons.append([InlineKeyboardButton(text="Удалить администратора", callback_data="del_admin")])
    buttons.append([InlineKeyboardButton(text="В меню", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "Да", txt_n: str = "Нет", cd_y: str = "yes"):
    buttons = [
        [InlineKeyboardButton(text=txt_y, callback_data=cd_y)],
        [InlineKeyboardButton(text=txt_n, callback_data="no")],
        [InlineKeyboardButton(text="Отмена", callback_data="admin")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def create_choose_city_buttons(state: FSMContext) -> InlineKeyboardBuilder:
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


def choice_people():
    buttons = [
        [InlineKeyboardButton(text="Курьеры", callback_data="notif_courier")],
        [InlineKeyboardButton(text="Заказчики", callback_data="notif_customer")],
        [InlineKeyboardButton(text="Все", callback_data="notif_all")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="admin")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_choice_people():
    buttons = [
        [InlineKeyboardButton(text="Курьеры", callback_data="view_courier")],
        [InlineKeyboardButton(text="Заказчики", callback_data="view_customer")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def del_admin(admins: list):
    buttons = []
    for i in admins:
        buttons.append([InlineKeyboardButton(text=i["username"], callback_data=f"del_{i['user_id']}")])
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_edit_record(check_cust: bool):
    buttons = [
        [
            InlineKeyboardButton(text="ФИО", callback_data="edit-fio"),
            InlineKeyboardButton(text="Телефон", callback_data="edit-phone"),
         ],
        [
            InlineKeyboardButton(text="Почта", callback_data="edit-email"),
            InlineKeyboardButton(text="Город", callback_data="edit-city")
        ]
    ]
    if check_cust:
        buttons.append([InlineKeyboardButton(text="Компания", callback_data="edit-organization")])
    buttons.append([InlineKeyboardButton(text="Удалить", callback_data="deleted-record")])
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="admin")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def courier_finish(id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Отмена",
        callback_data=f"finish_courier_{id}"
    ))
    return builder


def create_form_buttons(id: int):
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

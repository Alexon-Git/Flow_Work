from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.callback_data import CallbackData

from core.settings import settings
from core.database.database import get_id_admin

class VerificationKeyboard(CallbackData, prefix="verification"):
    mode:bool
    id:int

class StartFinishCourier(CallbackData, prefix="requestwork"):
    action:str
    request_id:int
    customer_message_id:int

class AddScore(CallbackData, prefix="addscore"):
    score:int
    courier_id:int
    request_id:int

class Chat(CallbackData, prefix="chat"):
    user_id:int
    code:str
class AnswerChat(CallbackData, prefix="readchat"):
    user_id: int
    request_code: str

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
    builder.row(InlineKeyboardButton(
        text="Написать в поддержку",
        callback_data="support")
    )
    if user_id in (await get_id_admin()):
        builder.row(InlineKeyboardButton(text='Администратору', callback_data="admin"))
    return builder


def create_courier_buttons(registration: bool, link=None) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Назад",
        callback_data=f"start")
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
        builder.add(InlineKeyboardButton(
            text="Активная заявка",
            callback_data=f"couriergetactiverequest"
        ))
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
        callback_data=f"start")
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

def answer_chat_button(user_id: int, code: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Прочитано", callback_data=AnswerChat(user_id = user_id, request_code = code).pack()),
         InlineKeyboardButton(text="Ответить",callback_data=Chat(user_id=user_id,code=code).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_form_button()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Отмена",callback_data="cancel_form"))
    return builder

def create_none_store_button()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Не из магазина.",callback_data="none_store"))
    builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel_form"))
    return builder

def add_score_button(courier_id:int,request_id:int)->InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="1", callback_data=AddScore(score = 1,courier_id =courier_id,request_id = request_id).pack()),
         InlineKeyboardButton(text="2", callback_data=AddScore(score = 2,courier_id =courier_id,request_id = request_id).pack()),
         InlineKeyboardButton(text="3", callback_data=AddScore(score = 3,courier_id =courier_id,request_id = request_id).pack()),
         InlineKeyboardButton(text="4", callback_data=AddScore(score = 4,courier_id =courier_id,request_id = request_id).pack()),
         InlineKeyboardButton(text="5", callback_data=AddScore(score = 5,courier_id =courier_id,request_id = request_id).pack())
         ],
        [InlineKeyboardButton(text="Завершить", callback_data=AddScore(score = 0,courier_id =courier_id,request_id = request_id).pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def translatelocation_buttons(user_id:int,code:str)->InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Доставил", callback_data="finishrequest")],[
         InlineKeyboardButton(text="Начать чат", callback_data=Chat(user_id=user_id,code=code).pack())]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def start_chat_button(user_id:int,code:str)->InlineKeyboardMarkup:
    button = [[InlineKeyboardButton(text="Начать чат", callback_data=Chat(user_id=user_id,code=code).pack())]]
    return InlineKeyboardMarkup(inline_keyboard=button)

def verification_courier_button(id:int)->InlineKeyboardMarkup:
    buttons=[
        [
        InlineKeyboardButton(text="Верифицировать",callback_data=VerificationKeyboard(mode = True,id = id).pack()),
        InlineKeyboardButton(text="Отказать",callback_data=VerificationKeyboard(mode = False,id = id).pack())]
    ]
    keyboard=InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def link_city_buttons(link:str)->InlineKeyboardBuilder:
    button = [[
        InlineKeyboardButton(text="Назад в меню", callback_data="start")
    ],[
        InlineKeyboardButton(text="Вступить в группу", url=link)
    ]]
    keyboard=InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard
def create_newform_button(link:str)->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Новая заявка",
        callback_data="customer_newform")
    )
    builder.add(InlineKeyboardButton(
        text="Мои заявки",
        callback_data=f"customer_forms")
    )
    builder.row(InlineKeyboardButton(text="Вступить в группу", url=link))
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
        callback_data="cancel_form"
    ))
    return builder


def admin_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Рассылка сообщений по пользователям", callback_data="notif")],
        [InlineKeyboardButton(text="Изменить стартовое сообщение", callback_data="edit_start_mess")],
        [InlineKeyboardButton(text="Изменить стоимость подписки", callback_data="edit_amount")],
        [InlineKeyboardButton(text="Просмотр Заказчиков/Курьеров", callback_data="view_record")],
        [InlineKeyboardButton(text="Просмотр статистики", callback_data="view_statistics")],
        [InlineKeyboardButton(text="Мин. и сред. ставка", callback_data="bet")],
        [InlineKeyboardButton(text="Обновить список городов", callback_data="update_city")]
    ]
    if user_id == settings.bots.admin_id:
        buttons.append([InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"),
                        InlineKeyboardButton(text="Удалить админа", callback_data="del_admin")])
    buttons.append([InlineKeyboardButton(text="В меню", callback_data="start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirmation(txt_y: str = "Да", txt_n: str = "Нет",
                 cd_y: str = "yes", cd_n: str = "no",
                 canc_data: str = "admin"):
    buttons = [
        [
            InlineKeyboardButton(text=txt_y, callback_data=cd_y),
            InlineKeyboardButton(text=txt_n, callback_data=cd_n)
        ],
        [InlineKeyboardButton(text="Отмена", callback_data=canc_data)]
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
        callback_data=f"cancel_form")
    )
    builder.add(InlineKeyboardButton(
        text="-->",
        callback_data=f"city_next")
    )
    return builder

def state_cancel()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отменить действие",callback_data="state_cancel"))
    return builder


def status_work()->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="В работе",
        callback_data="none"
    ))
    return builder


def form_cancel_chat(id:int,user_id:int,code:str)->InlineKeyboardMarkup:
    buttons =  [
        [InlineKeyboardButton(text="Начать чат",callback_data=Chat(user_id=user_id,code=code).pack())],
        [InlineKeyboardButton(text="Отменить заявку",callback_data=f"formcancel_{id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
        [InlineKeyboardButton(text="Все", callback_data="notif_all")],
        [InlineKeyboardButton(text="Отмена", callback_data="admin")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel_admin():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="admin")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_choice_people():
    buttons = [
        [InlineKeyboardButton(text="Курьеры", callback_data="view_courier")],
        [InlineKeyboardButton(text="Заказчики", callback_data="view_customer")],
        [InlineKeyboardButton(text="Отмена", callback_data="admin")]
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


def courier_start_finish(id: int,message_id:int,user_id:int,code:str):
    buttons = [
        [InlineKeyboardButton(text="Принял товар",callback_data=StartFinishCourier(action="start",request_id=id, customer_message_id = message_id).pack())],
        [InlineKeyboardButton(text="Отмена",callback_data=StartFinishCourier(action="finish",request_id=id, customer_message_id = message_id).pack())],
        [InlineKeyboardButton(text="Начать чат",callback_data=Chat(user_id=user_id,code=code).pack())]
    ]
    # builder = InlineKeyboardBuilder()
    # builder.(InlineKeyboardButton(
    #     text="Принял товар",
    #     callback_data=f"sadstart_courier_{id}"
    # ))
    # builder.row(InlineKeyboardButton(
    #     text="Отмена",
    #     callback_data=f"finish_courier_{id}"
    # ))
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_form_buttons(id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Откликнуться",
        callback_data=f"request_{id}"
    ))
    builder.row(InlineKeyboardButton(
        text="Задать вопрос",
        callback_data=f"request-chat_{id}"
    ))
    return builder



def edit_bet():
    buttons = [
        [InlineKeyboardButton(text="Изменить", callback_data="bet_edit")],
        [InlineKeyboardButton(text="Отмена", callback_data="admin")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_choose_city_buttons_stat(n: int, city: list):
    n-=1
    n*=6
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
        callback_data=f"cancel_form")
    )
    builder.add(InlineKeyboardButton(
        text="-->",
        callback_data=f"city_next")
    )
    return builder.as_markup()


def custom_btn(text: str, cldata: str):
    buttons = [[InlineKeyboardButton(text=text, callback_data=cldata)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def information():
    buttons = [[InlineKeyboardButton(text="Посмотреть инструкцию", web_app=WebAppInfo(
        url="https://nil-it.notion.site/Flowwork-e71f09ba455f4fa8a5df000e92265374?pvs=4"))]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


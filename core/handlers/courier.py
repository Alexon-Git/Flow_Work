import math
import datetime
from datetime import date

from aiogram import Router, types, F, Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import LabeledPrice, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import StorageKey
from core.keyboards.reply import *
from aiogram import types


from core.filters.Filters import *
from core.database import database
from core.keyboards.inline import *
from core.message.text import get_amount
from core.settings import city_info


from aiogram.fsm.context import FSMContext

router = Router()

REDIS_DSN = "redis://127.0.0.1:6379"

from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
storage = RedisStorage.from_url(REDIS_DSN, key_builder=DefaultKeyBuilder(with_bot_id=True),
                                data_ttl=datetime.timedelta(days=1.0), state_ttl=datetime.timedelta(days=1.0))
dp = Dispatcher(storage=storage)


class CourierState(StatesGroup):
    fio = State()
    email = State()
    city = State()
    phone = State()
    photo = State()
    n = ()
#msg = await message.answer(f"Регистрация успешно завершена.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nПрежде чем вы получите 14д пробного использования администраторы должны проверить ваш профиль.В стартовом меню в разделе 'Курьер' вы можете продлить подписку.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nСсылка на вступление в группу города: {link.invite_link}",reply_markup=ReplyKeyboardRemove())

@router.callback_query(F.data == "courier")
async def courier_callback(callback: types.CallbackQuery, bot: Bot):
    if await database.check_courier(user_id=callback.from_user.id):
        expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
        courier = await database.get_courier(callback.from_user.id)
        if courier["verification"] == False:
            await callback.answer(
                "Меню курьеров будет недоступно до окончания верификации. Просим прощения за ожидание.")
            return
        chat_id = 0
        link = ""
        for i in city_info.city_info:
            if i["Город"] == courier["city"]:
                link = i["ссылка"]
        builder = create_courier_buttons(True, link)

        days = datetime.datetime.strptime(courier["date_payment_expiration"], "%Y-%m-%d").date() - date.today()
        if days.days < 0:
            message = f"Меню для курьеров.\nУ вас закончилась подписка."
        else:
            message = f"Меню для курьеров.\nУ вас осталось {days.days}д. оплаченной подписки."
    else:
        message = "Меню для курьеров.\nПройдите регистрацию и вы получите 14д. пробного периода."
        builder = create_courier_buttons(False)
    await callback.message.edit_text(text=message, reply_markup=builder.as_markup())




#===================================Колбек Меню Курьера===================================
@router.callback_query(F.data.startswith("courier_"))
async def courier_button_callback(callback: types.CallbackQuery,state: FSMContext,bot: Bot):
    action = callback.data.split("_")[1]

    if action == "registration":
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.set_state(CourierState.fio)
        await callback.message.answer("Введите ваше ФИО (Формат: 3 слова 'Ф И О')")
        await callback.answer()
    elif action == "getactiverequest":
        form = await database.get_courier_active_request(callback.from_user.id)
        if form is None:
            await callback.answer("У вас нет активных заявок.")
            return
        for i in range(len(form)-1):
            status = form[f'status_work_{i}']
            code = form[f'code_{i}']
            msg = "<b>Активная заявка</b>"
            msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            msg += f"Магазин: {form[f'store_name_{i}']}\n"
            adress_a =form[f'adress_a_{i}']
            adress_b = form[f'adress_b_{i}']
            msg += f"Адрес А:  <code>{adress_a}</code>\n"
            msg += f"Адрес Б:  <code>{adress_b}</code>\n"
            msg += f"Стоимость: {form[f'price_{i}']}\n"
            msg += f"Код: {form[f'code_{i}']}\n"
            if status == 'work':
                kb = [
                    [InlineKeyboardButton(text='Заказ уже у вас в работе', callback_data='cal')],
                    [types.InlineKeyboardButton(text='Отказаться', callback_data=f'refuse {code}')],
                    [types.InlineKeyboardButton(text='Прибыл в магазин', callback_data=f'arivved_to_shop {code}')],
                    [types.InlineKeyboardButton(text='Изменить', callback_data=f'edit_courier {code}')]
                ]
                markup = InlineKeyboardMarkup(inline_keyboard=kb)
                msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                             reply_markup=markup)
                await callback.answer()
            elif status == 'shop':
                kb = [
                    [types.InlineKeyboardButton(text='Забрал заказ', callback_data=f'get_order {code}')],
                    [types.InlineKeyboardButton(text='Отказаться', callback_data=f'refuse {code}')]
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
                msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                             reply_markup=keyboard)
                await callback.answer()
            elif status == 'get_order':
                kb = [
                    [types.InlineKeyboardButton(text='Прибыл к получателю', callback_data=f'arrived {code}')]
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
                msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                             reply_markup=keyboard)
                await callback.answer()
            elif status == 'arrived':
                kb = [
                    [types.InlineKeyboardButton(text='Закрыть', callback_data=f'close_request {code}')]
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
                msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                             reply_markup=keyboard)
                await callback.answer()
            elif status == 'sent':
                keyboard = [
                    [InlineKeyboardButton(text='Закрыть', callback_data='deletecallmes')],
                    [InlineKeyboardButton(text='Взять', callback_data=f'take_orders {form[f"code_{i}"]}')]
                ]
                buttons = InlineKeyboardMarkup(inline_keyboard=keyboard)
                msg = await bot.send_message(chat_id=callback.from_user.id, text=msg,
                                             reply_markup=buttons)
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

#===================================Удаление активной заявки===================================
@router.callback_query(F.data == "deletecallmes")
async def deletecallmes(callback: types.CallbackQuery):
    await callback.message.delete()

@router.callback_query(F.data.startswith("take_orders"))
async def take_orders(callback: types.CallbackQuery, bot: Bot):
    code = callback.data.split()[1]
    courier_id = callback.from_user.id
    courier_name = callback.from_user.username
    await database.request_work_into_db(code, courier_id)
    kb = [
        [InlineKeyboardButton(text='Заказ уже у вас в работе', callback_data='cal')],
        [types.InlineKeyboardButton(text='Отказаться', callback_data=f'refuse {code}')],
        [types.InlineKeyboardButton(text='Прибыл в магазин', callback_data=f'arivved_to_shop {code}')],
        [types.InlineKeyboardButton(text='Изменить', callback_data=f'edit_courier {code}')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.message.answer(f'Вы успешно взяли заказ с кодом {code}!')
    buttons = [
        [InlineKeyboardButton(text='Управление', callback_data=f"add_buttons {code}")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(settings.bots.admin_id, f'Курьер: @{courier_name}\n ID: {courier_id}. \n Статус: Принят в работу \n Код: {code}\n  Изменить:', reply_markup=markup)
    await database.into_in_orders(courier_id, code)


@router.callback_query(F.data.startswith('close_request'))
async def close_request(callback: types.CallbackQuery, bot: Bot):
    code = callback.data.split()[1]
    courier_name = callback.from_user.username
    await database.request_work_finish_db(code=code)
    courier_id = callback.from_user.id
    kb = [
        [InlineKeyboardButton(text='Заказ закрыт', callback_data='ccc')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.send_message(settings.bots.admin_id, f'Заказ с кодом: {code} \n Статус: Закрыт курьером \n ID курьера: {courier_id} \n Ник: @{courier_name}')
    keyboard = ReplyKeyboardRemove()
    await callback.message.answer('Вы успешно закрыли заказ!', reply_markup=keyboard)
    await callback.message.edit_reply_markup(reply_markup=markup)

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
    for i in city_info.city_info:
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



#===================================Номер===================================
@router.message(CourierState.phone,(F.contact!=None and F.contact.user_id == F.from_user.id))
async def courier_contact(message:Message,state: FSMContext,bot:Bot):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Последний этап: отправьте фотографию документа, подтверждающего личность. Документ должен быть читабельным для вашей успешной верификации",reply_markup=ReplyKeyboardRemove())
    await state.set_state(CourierState.photo)
@router.message(CourierState.phone)
async def courier_contact_message(message:Message,state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Последний этап: отправьте фотографию документа, подтверждающего личность. Документ должен быть читабельным для вашей успешной верификации",reply_markup=ReplyKeyboardRemove())
    await state.set_state(CourierState.photo)

#===================================Фотография документа и завершение регистрации===================================
@router.message(CourierState.photo, F.photo !=None)
async def courier_photo(message: Message,state:FSMContext,bot:Bot):
    await state.update_data(photo = message.photo[1].file_id)

    data = await state.get_data()
    await state.clear()
    link = city_info.city_info[data["city"]]["ссылка"]
    await message.answer(f"Регистрация успешно завершена.\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nПрежде чем вы получите 14д пробного использования и сможете отвечать на заявки, администраторы должны проверить ваш профиль.", reply_markup=link_city_buttons(link))
    new_courier = {
        "username": message.from_user.first_name,
        "user_id": message.from_user.id,
        "status_payment": True,
        "date_payment_expiration": "",
        "date_registration": str(date.today()),
        "fio": data["fio"],
        "city": city_info.city_info[data["city"]]["Город"],
        "phone": data["phone"],
        "email": data["email"],
        "notification_one": None,
        "notification_zero": None,
        "verification": False
    }
    await database.set_courier(new_courier)
    msg = "ВЕРИФИКАЦИЯ КУРЬЕРА"
    msg += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    msg += f"Пользователь: @{message.from_user.username}\n"
    msg += f"Ссылка: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
    await bot.send_photo(chat_id=settings.bots.chat_id, photo=data["photo"], caption=msg,parse_mode="Markdown",reply_markup=verification_courier_button(message.from_user.id))



#===================================Верификация курьера===================================
@router.callback_query(VerificationKeyboard.filter())
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: VerificationKeyboard,bot:Bot):
    if callback_data.mode:
        data =str(date.today()+datetime.timedelta(days=14))
        await database.verification_courier(callback_data.id,data)
        text= "Вы успешно прошли верификацию. Теперь вы имеете возможность откликаться на заявке в группе вашего города.\nБлагодарим за ожидание."
        await bot.send_message(chat_id=callback_data.id,text=text)
    else:
        text = "Вы не прошли верификацию. Проверьте правильность введенных данных и корректность отправленной фотографии."
        await bot.send_message(chat_id=callback_data.id,text=text)
    await callback.message.delete()
    await callback.answer()



#===================================Задать вопрос===================================
class Question(StatesGroup):
    SetQuestion = State()


@router.callback_query(F.data.startswith("request-chat"))
async def request_chat(call: CallbackQuery, state: FSMContext, bot: Bot):
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
        await dp.storage.set_state(fsm_storage_key, Question.SetQuestion)
        await dp.storage.update_data(fsm_storage_key, data)
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
    city_info.update()
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

########################### ОБРАБОТЧИК СООБЩЕНИЙ ###############################
@router.callback_query(F.data.startswith('refuse'))
async def refuse(callback: types.CallbackQuery, bot: Bot):
    code = callback.data.split()[1]
    courier_id = callback.from_user.id
    courier_name = callback.from_user.username
    await database.request_work_close_db(code)
    keyboard = [
        [InlineKeyboardButton(text='Закрыть', callback_data='deletecallmes')],
        [InlineKeyboardButton(text='Взять', callback_data=f'take_orders {code}')]
    ]
    buttons = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await bot.send_message(settings.bots.admin_id, f'Курьер @{courier_name}\n ID: {courier_id}\n Статус: Активная(отказался от заказа) \n Код: {code}')
    await callback.message.answer(f'Вы отказались от заказа с кодом {code}')
    await database.refuse_db(courier_id)


@router.callback_query(F.data.startswith('arivved_to_shop'))
async def arrived_to_shop(callback: types.CallbackQuery, bot:Bot):
    code = callback.data.split()[1]
    courier_id = callback.from_user.id
    courier_name = callback.from_user.username
    kb = [
        [types.InlineKeyboardButton(text='Забрал заказ', callback_data=f'get_order {code}')],
        [types.InlineKeyboardButton(text='Отказаться', callback_data=f'refuse {code}')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await database.request_status_shop(code)
    await bot.send_message(settings.bots.admin_id, f"Курьер: @{courier_name}\n ID: {courier_id}. \n Статус: Прибыл в магазин \n Код: {code}")
    await callback.message.answer("Принято")
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await database.arrived_to_shop_db(courier_id)


@router.callback_query(F.data.startswith('get_order'))
async def get_order(callback: types.CallbackQuery, bot: Bot):
    code = callback.data.split()[1]
    courier_id = callback.from_user.id
    courier_name = callback.from_user.username
    kb = [
        [types.InlineKeyboardButton(text='Прибыл к получателю', callback_data=f'arrived {code}')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await database.request_status_get_order(code)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await bot.send_message(settings.bots.admin_id, f'Курьер: @{courier_name}\n ID: {courier_id}. \n Статус: Забрал заказ \n Код: {code}')
    await callback.message.answer('Принято')
    await database.get_order_db(courier_id)


@router.callback_query(F.data.startswith('arrived'))
async def arrived_to_place(callback: types.CallbackQuery, bot:Bot):
    courier = callback.from_user.id
    courier_name = callback.from_user.username
    code = callback.data.split()[1]
    kb = [
        [types.InlineKeyboardButton(text='Закрыть', callback_data=f'close_request {code}')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await database.request_status_arrived(code)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await bot.send_message(settings.bots.admin_id, f'Курьер: @{courier_name}\n ID: {courier}. \n Статус: Прибыл к получателю \n Код: {code}')
    await callback.message.answer('Принято')
    await database.arrived_to_place_db(courier)


@router.callback_query(F.data.startswith('edit_courier'))
async def edit(callback:types.CallbackQuery):
    code = callback.data.split()[1]
    buttons = [
        [InlineKeyboardButton(text='Изменить время', callback_data=f"edit_time {code}")],
        [InlineKeyboardButton(text='Изменить адрес', callback_data=f"edit_place {code}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f'Выберите действие для заказа с кодом {code}:', reply_markup=keyboard)

class editer(StatesGroup):
    time = State()
    place = State()
    time_variable = ()


class edit_admin(StatesGroup):
    time_admin = State()
    place_admin_a = State()
    place_admin_b = State()
    money_admin = State()
    phone_customer = State()
    phone_executor = State()
    new_courier = State()
    new_status = State()
    time_variable = ()

@router.callback_query(F.data.startswith('edit_time'))
async def edit_time(callback: types.CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    kb = [
        [InlineKeyboardButton(text='Отменить действие', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer(f'Введите новое время для заказа \n Код: {code}:', reply_markup=keyboard)
    await state.set_state(editer.time)
    await state.update_data(time_variable=code)


@router.callback_query(F.data.startswith('edit_place'))
async def edit_place(callback: types.CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    kb = [
        [InlineKeyboardButton(text='Отменить действие', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer(f'Введите новое место для заказа \n Код: {code}:', reply_markup=keyboard)
    await state.set_state(editer.place)
    await state.update_data(time_variable=code)


@router.message(editer.time)
async def edite_time_state(message:types.Message, state: FSMContext, bot:Bot):
    text = message.text
    data = await state.get_data()
    await state.clear()
    code = data["time_variable"]
    await bot.send_message(settings.bots.admin_id, f'Время заказа с кодом {code} изменено на: \n {text}')
    await message.answer(f'Время изменено на: \n {text} \n Код: {code}')

@router.message(editer.place)
async def edite_place_state(message: types.Message, state:FSMContext, bot:Bot):
    data = await state.get_data()
    code = data["time_variable"]
    place = message.text
    await database.new_place_b(code, place)
    await bot.send_message(settings.bots.admin_id, f"Место заказа с кодом {code} изменено на: \n {place}")
    await message.answer(f'Место изменено на: \n {place}, \n Код: {code}')
    await state.clear()



########################################################################
@router.callback_query(F.data.startswith('time_admin'))
async def edit_time_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    kb = [
        [InlineKeyboardButton(text='Отменить действие', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer(f'Введите время Код: {code}:', reply_markup=keyboard)
    await state.set_state(edit_admin.time_admin)
    await state.update_data(time_variable=code)


@router.message(edit_admin.time_admin)
async def admin_time(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    cod = data['time_variable']
    new_time = message.text
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Время заказа изменено на {new_time}, \n Код: {cod}')
    await state.clear()


@router.callback_query(F.data.startswith('place_a_admin'))
async def edit_place_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    kb = [
        [InlineKeyboardButton(text='Отменить действие', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer(f'Введите новый адрес A \n Код: {code}:', reply_markup=keyboard)
    await state.set_state(edit_admin.place_admin_a)
    await state.update_data(time_variable=code)


@router.message(edit_admin.place_admin_a)
async def admin_place(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    cod = data['time_variable']
    new_place = message.text
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Адрес A заказа изменен на {new_place}, \n Код: {cod}')
    await database.new_place_a(cod, new_place)
    await state.clear()

@router.callback_query(F.data.startswith('place_b_admin'))
async def edit_place_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    await callback.message.answer(f'Введите новый адрес B \n Код: {code}:', reply_markup=close_state_fun())
    await state.set_state(edit_admin.place_admin_b)
    await state.update_data(time_variable=code)


@router.message(edit_admin.place_admin_b)
async def admin_place(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    cod = data['time_variable']
    new_place = message.text
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Адрес B заказа изменен на {new_place}, \n Код: {cod}')
    await database.new_place_b(cod, new_place)
    await state.clear()



@router.callback_query(F.data.startswith('phone_customer'))
async def edit_phone_customer_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    await callback.message.answer(f'Введите новый телефон заказчика: \n Код: {code}', reply_markup=close_state_fun())
    await state.set_state(edit_admin.phone_customer)
    await state.update_data(time_variable=code)


@router.message(edit_admin.phone_customer)
async def admin_phone_customer(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    cod = data["time_variable"]
    new_place = message.text
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Телефон заказчика изменен на {new_place}, \n Код: {cod}')
    await state.clear()


@router.callback_query(F.data.startswith('phone_executor'))
async def edit_phone_executor_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    await callback.message.answer(f'Введите новый телефон исполнителя: \n Код: {code}', reply_markup=close_state_fun())
    await state.set_state(edit_admin.phone_executor)
    await state.update_data(time_variable=code)


@router.message(edit_admin.phone_executor)
async def admin_phone_executor(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    cod = data['time_variable']
    new_place = message.text
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Телефон исполнителя изменен на {new_place}, \n Код: {cod}')
    await state.clear()

@router.callback_query(F.data.startswith('money_admin'))
async def edit_money_admin(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    kb = [
        [InlineKeyboardButton(text='Отменить действие', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.answer(f'Введите новую сумму: \n Код: {code}', reply_markup=keyboard)
    await state.set_state(edit_admin.money_admin)
    await state.update_data(time_variable=code)


@router.message(edit_admin.money_admin)
async def money_admin(message: types.Message, state: FSMContext,bot:Bot):
    data = await state.get_data()
    cod = data['time_variable']
    new_money = int(message.text)
    courier_id = await database.get_courier_id_for_code(cod)
    await bot.send_message(courier_id, f'Сумма заказа изменена на {new_money},\n Код: {cod}')
    await database.request_update_money(cod, new_money)
    await state.clear()


@router.callback_query(F.data.startswith('send_courier'))
async def admin_send_courier(callback:CallbackQuery, state: FSMContext):
    code = callback.data.split()[1]
    await callback.message.answer(f'Введите новый id курьера \n Код: {code}', reply_markup=close_state_fun())
    await state.set_state(edit_admin.new_courier)
    await state.update_data(time_variable=code)


@router.message(edit_admin.new_courier)
async def send_courier(message: types.Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    code = data['time_variable']
    await state.clear()
    courier_id = message.text
    kb = [
        [InlineKeyboardButton(text='Заказ уже у вас в работе', callback_data='cal')],
        [types.InlineKeyboardButton(text='Отказаться', callback_data=f'refuse {code}')],
        [types.InlineKeyboardButton(text='Прибыл в магазин', callback_data=f'arivved_to_shop {code}')],
        [types.InlineKeyboardButton(text='Изменить', callback_data=f'edit_courier {code}')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.send_message(courier_id, f'Вам был передан заказ с кодом: {code}', reply_markup=keyboard)
    await database.new_courier_request(code, courier_id)
    await database.new_courier_db(code, courier_id)




@router.callback_query(F.data.startswith('admin_active'))
async def admin_active(callback: types.CallbackQuery):
    cod = callback.data.split(' ')[1]
    await database.admin_request_active(cod)
    await callback.message.answer(f'Заказ перемещен в активные, \n Код: {cod}')
    await database.active_order_db_admin(cod)


@router.callback_query(F.data.startswith('admin_close'))
async def admin_close(callback: types.CallbackQuery):
    cod = callback.data.split(' ')[1]
    await database.admin_request_close(cod)
    await callback.message.answer(f'Заказ перемещен в завершенные, \n Код: {cod}')
    await database.close_order_db_admin(cod)

@router.callback_query(F.data == 'close_state')
async def close_state(callback: CallbackQuery, state:FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await callback.answer("Ожидание ответа успешно отменено.")
    await callback.message.delete()

@router.message(F.text.lower() == 'отмена')
async def close_state(message: types.Message):
    kb = [
        [InlineKeyboardButton(text='Отменить ожидание', callback_data='close_state')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer('Отменить ожмдание', reply_markup=keyboard)










import asyncio
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup

import core.keyboards.inline as kbi
from core.google_doc.googleSheets import creat_table
import core.database.database as db


subrouter = Router()


class EditRecord(StatesGroup):
    ChoiceId = State()
    SetData = State()
    CheckMessage = State()
    DeletedRecord = State()


@subrouter.callback_query(F.data == "view_record")
async def view_records(call: CallbackQuery):
    await call.message.edit_text(f"Выберите тип записей:", reply_markup=kbi.admin_choice_people())


@subrouter.callback_query(F.data == "view_customer")
@subrouter.callback_query(F.data == "view_courier")
async def choice_id_records(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Ожидайте, таблица готовится!")
    try:
        await creat_table(call.data.split("_")[-1])
        msg = await call.message.edit_text("Существующие записи:\n"
                                     "https://docs.google.com/spreadsheets/d/1ZdLjtdhlsD3B1wVDQFRfTo3NpvqGyudoitUJLcBuSNo/edit#gid=1109808180\n\n"
                                     "Введите TG_ID нужного человека для редактирования", reply_markup=kbi.cancel())
        await state.set_state(EditRecord.ChoiceId)
        await state.update_data({"del":msg.message_id, "type": call.data.split("_")[-1]})
    except IndexError:
        await call.message.edit_text("В базе отсутствуют записи для данного раздела",
                                     reply_markup=kbi.admin_menu(call.from_user.id))


@subrouter.callback_query(F.data == "no", EditRecord.DeletedRecord)
@subrouter.callback_query(F.data == "no", EditRecord.CheckMessage)
async def choice_id_records(call: CallbackQuery, state: FSMContext):
        msg = await call.message.edit_text("Существующие записи:\n"
                                     "https://docs.google.com/spreadsheets/d/1ZdLjtdhlsD3B1wVDQFRfTo3NpvqGyudoitUJLcBuSNo/edit#gid=1109808180\n\n"
                                     "Введите TG_ID нужного человека для редактирования", reply_markup=kbi.cancel())
        await state.update_data({"del": msg.message_id})
        await state.set_state(EditRecord.ChoiceId)


@subrouter.message(EditRecord.ChoiceId)
async def view_data_record(mess: Message, state: FSMContext, bot: Bot):
    try:
        del_kb = (await state.get_data())["del"]
        await bot.edit_message_reply_markup(mess.chat.id, del_kb, reply_markup=None)
    except:
        pass
    try:
        check_cust = await db.check_customer(int(mess.text))
        check_cour = await db.check_courier(int(mess.text))
        if check_cour:
            data_record = await db.get_courier(int(mess.text))
        elif check_cust:
            data_record = await db.get_customer(int(mess.text))
        else:
            await mess.answer("Такого пользователя нет в базе данных!")
            return
        text_mess = ("Информация:\n"
                     f"ФИО: {data_record['fio']}\n"
                     f"Телефон: {data_record['phone']}\n"
                     f"Почта: {data_record['email']}\n"
                     f"Город: {data_record['city']}\n")
        if check_cust:
            text_mess += f"Компания: {data_record['organization']}"
        text_mess += "\nМожно изменить:"
        await mess.answer(text_mess, reply_markup=kbi.admin_edit_record(check_cust))
        await state.update_data({"user_id": int(mess.text)})
    except:
        await mess.answer("Данные не являются telegram_id!")


@subrouter.callback_query(F.data.split("-")[0] == "edit", EditRecord.ChoiceId)
async def set_new_data_record(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите новые данные!", reply_markup=kbi.cancel())
    await state.update_data({"fild": call.data.split("-")[-1]})
    await state.set_state(EditRecord.SetData)


@subrouter.message(EditRecord.SetData)
async def check_new_data_record(mess: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data["type"] == "courier":
        data_record = await db.get_courier(data["user_id"])
    else:
        data_record = await db.get_customer(data["user_id"])
    new_data_record = {}
    for i in data_record.keys():
        new_data_record[i] = data_record[i]
    new_data_record[data["fild"]] = mess.text
    text_mess = ("Информация:\n"
                 f"ФИО: {new_data_record['fio']}\n"
                 f"Телефон: {new_data_record['phone']}\n"
                 f"Почта: {new_data_record['email']}\n"
                 f"Город: {new_data_record['city']}\n")
    if data["type"] == "customer":
        text_mess += f"Компания: {new_data_record['organization']}"
    await mess.answer("Новые данные:\n"+text_mess+"\nСохраняем изменения?", reply_markup=kbi.confirmation())
    await state.update_data(new_data_record)
    await state.set_state(EditRecord.CheckMessage)


@subrouter.callback_query(F.data == "yes", EditRecord.CheckMessage)
async def deleted_record(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data["type"] == "courier":
        await db.update_courier(data)
    else:
        await db.update_customer(data)
    await call.message.edit_text("Данные обновлены!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()


@subrouter.callback_query(F.data == "yes", EditRecord.DeletedRecord)
async def deleted_record(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data["type"] == "courier":
        await db.deleted_courier(data["user_id"])
    else:
        await db.deleted_customer(data["user_id"])
    await call.message.edit_text("Запись удалена!", reply_markup=kbi.admin_menu(call.from_user.id))
    await state.clear()

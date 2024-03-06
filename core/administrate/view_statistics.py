import math
import datetime as dt

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters.state import State, StatesGroup

from core.keyboards import inline as kbi
from core.google_doc.googleSheets import upload_statistics
from core.settings import city_info, scheduler
from core.statistics.basic import get_statistic, clean_statistic

router = Router()


class ViewStat(StatesGroup):
    views = State()


@router.callback_query(F.data == "back")
@router.callback_query(F.data == "view_statistics")
async def menu_admins(call: CallbackQuery, state: FSMContext):
    cities = []
    for i in city_info:
        if i["Город"] != "":
            cities.append(i["Город"])
        else:
            break
    await state.set_data({"n": 1, "city": cities})
    await call.message.edit_text("Выберите город:", reply_markup=kbi.create_choose_city_buttons_stat(1, cities))


@router.callback_query(F.data == "city_next" or F.data == "city_back")
async def menu_admins(call: CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]
    if action == "next":
        data = await state.get_data()
        n = data["n"]
        city = data['city']
        if n + 1 > math.ceil(len(city) / 6):
            await call.answer("Это конец списка")
            return
        else:
            n += 1
        await state.update_data(n=n)
        await call.message.edit_reply_markup(reply_markup=kbi.create_choose_city_buttons_stat(n, city))
    elif action == "back":
        data = await state.get_data()
        n = data["n"]
        city = data['city']
        if n - 1 < 1:
            await call.answer("Это начало списка")
            return
        else:
            n -= 1
        await state.update_data(n=n)
        await call.message.edit_reply_markup(reply_markup=kbi.create_choose_city_buttons_stat(n, city))


@router.callback_query(F.data.split("_")[0] == "city")
async def menu_admins(call: CallbackQuery):
    action = call.data.split("_")[1]
    city_id = city_info[int(action)]["chat id"]
    try:
        data = get_statistic(city_id)
        await call.message.edit_text(f"Статистика по городу {city_info[int(action)]['Город']}\n"
                                     f"за {dt.date.strftime(dt.date.today(), '%d.%m.%Y')}\n"
                                     f"Новые заявки: {data['record_new']}\n"
                                     f"Отмененные заявки: {data['record_cancel']}\n"
                                     f"Завершенные заявки: {data['record_done']}\n",
                                     reply_markup=kbi.custom_btn("Назад", "back"))
    except FileNotFoundError:
        await call.answer("Статистика для данного города отсутствует")


@scheduler.scheduled_job("cron", hour=23, minute=58)
async def upload_stat():
    for i in city_info.city_info:
        upload_statistics(i["Город"], i["chat id"])
        clean_statistic(i["chat id"])

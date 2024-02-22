import datetime as dt
from core.settings import sheet, city_info
from core.statistics.basic import get_statistic
from core.database.database import get_all_customer, get_all_courier


def get_id_admin() -> list:
    worksheet = sheet.worksheet("admins")
    values_list = worksheet.get_all_values()
    return [int(i[0]) for i in values_list[1:]]


async def creat_table(type_people: str):
    worksheet = sheet.worksheet("records")
    worksheet.clear()
    if type_people == "customer":
        records = await get_all_customer()
    else:
        records = await get_all_courier()
    worksheet.append_row([j for j in records[0].keys()])
    for i in records:
        worksheet.append_row([j for j in i.values()])


def upload_statistics(city_name: str, city_id: int):
    worksheet = sheet.worksheet("Statistic")
    data = get_statistic(city_id)
    worksheet.append_row([dt.date.strftime(dt.date.today(), '%d.%m.%Y'),
                          city_name, data["record_new"], data["record_cancel"], data["record_done"]])
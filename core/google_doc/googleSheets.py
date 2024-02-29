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
        cour = False
    else:
        records = await get_all_courier()
        cour = True
    heading = [j for j in records[0].keys()]
    if cour:
        heading.pop(-1)
        heading.pop(-1)
        heading.append("score")
    worksheet.append_row(heading)
    for i in records:
        tmp_row = [j for j in i.values()]
        if cour:
            try:
                tmp_score = tmp_row[-1]/tmp_row[-2]
            except ZeroDivisionError:
                tmp_score = 0
            tmp_row.pop(-1)
            tmp_row.pop(-1)
            tmp_row.append(tmp_score)
        worksheet.append_row(tmp_row)


def upload_statistics(city_name: str, city_id: int):
    worksheet = sheet.worksheet("Statistic")
    data = get_statistic(city_id)
    worksheet.append_row([dt.date.strftime(dt.date.today(), '%d.%m.%Y'),
                          city_name, data["record_new"], data["record_cancel"], data["record_done"]])

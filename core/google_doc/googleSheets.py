import gspread
from google.oauth2.service_account import Credentials
from core.settings import home, sheet



# def get_id_admin() -> list:
#     worksheet = sheet.worksheet("admins")
#     values_list = worksheet.get_all_values()
#     return [int(i[0]) for i in values_list[1:]]


def get_id_admin() -> list:
    return [1235360344]

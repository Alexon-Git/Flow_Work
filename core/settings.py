# pip install environs
# import gspread
import os
from environs import Env
from dataclasses import dataclass

import gspread
from google.oauth2.service_account import Credentials

from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# Путь от корня системы до папки core например:
# D:\Programing\Flow_Work\core
home = os.path.dirname(__file__)

@dataclass
class Bots:
    bot_token: str
    admin_id: int
    chat_id: int
    # admin_id_2: int

@dataclass
class Settings:
    bots: Bots
    db_user: str
    db_password: str
    yandex_api:str

def get_settings(path: str):
    evn = Env()
    evn.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=evn.str("BOT_TOKEN"),
            admin_id=evn.int("ADMIN_ID"),
            chat_id=evn.int("CHAT_ID")
        ),
        db_user=evn.str("DB_USER"),
        db_password=evn.str("DB_PASSWORD"),
        yandex_api=evn.str("YANDEX_API")
    )

settings = get_settings('config')

scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/cred.json')
client = gspread.authorize(credentials.with_scopes(scope))
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1ZdLjtdhlsD3B1wVDQFRfTo3NpvqGyudoitUJLcBuSNo/edit#gid=0')
worksheet_city = sheet.worksheet('City')

class Cities():
    def __init__(self):
        self.city_info = worksheet_city.get_all_records()
    def update(self):
        self.city_info = worksheet_city.get_all_records()


city_info = Cities()

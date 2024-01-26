# pip install environs
import gspread
from environs import Env
from dataclasses import dataclass
from google.oauth2 import service_account

@dataclass
class Bots:
    bot_token: str
    admin_id: int
    # admin_id_2: int

@dataclass
class Settings:
    bots: Bots

def get_settings(path: str):
    evn = Env()
    evn.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=evn.str("BOT_TOKEN"),
            admin_id=evn.int("ADMIN_ID")
        )
    )

settings = get_settings('config')

# scope = ['https://www.googleapis.com/auth/spreadsheets']
# credentials = service_account.Credentials.from_service_account_file('core/cred.json')
# client = gspread.authorize(credentials.with_scopes(scope))
# sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/16XBlws6qIfZ7q9yPhqocrywvwZn4XBqYwrRoJLzJp2k/edit#gid=558743972')
# worksheet = sheet.get_worksheet(0)
# worksheet_user = sheet.worksheet('UserBot')
# worksheet_stocks = sheet.get_worksheet(2)


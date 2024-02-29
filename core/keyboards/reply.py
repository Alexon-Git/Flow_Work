from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_contact_button()->ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Поделиться номером", request_contact=True))
    return builder

def send_courier_location()->ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Поделиться местоположенем", request_location=True))
    return builder

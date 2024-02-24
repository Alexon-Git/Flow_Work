from aiogram.filters import BaseFilter
from aiogram.types import Message
import re
# from email_validate import validate


class FioFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool: 
        return len(message.text.split())==3


class EmailFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:  
        return "@" in message.text


def check_test(text: str) -> bool:
    regex = re.compile("\+?\d[\( -]?\d{3}[\) -]?\d{3}[ -]?\d{2}[ -]?\d{2}")
    numbers = re.findall(regex, text)
    phone = [] == numbers
    link = "html" in text or ".ru" in text or ".com" in text or "@" in text
    return phone and link


# check_test(";bnz'db;xfdobuznfdjbn89237066488dfvkjsnd;bkjsdn2-923-706-64-88dfbxfdbxb+79237066488 2 923 706 64 88djctvm")
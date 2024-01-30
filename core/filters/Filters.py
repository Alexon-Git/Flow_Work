from aiogram.filters import BaseFilter
from aiogram.types import Message
from email_validate import validate

class FioFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool: 
        return len(message.text.split())==3
class EmailFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:  
        return validate(message.text)
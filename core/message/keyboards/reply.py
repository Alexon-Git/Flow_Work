from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


but_catalog=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Каталог")
                    # KeyboardButton(text="Распродажа"),
                ],
                [
                    KeyboardButton(text="Отзывы"),
                    KeyboardButton(text="Нашли ошибку?")
                ],
                # [
                    # KeyboardButton(text="Нет в наличии?"),
                    # KeyboardButton(text="Контакты"),
                # ],
                [
                    KeyboardButton(text="Корзина")
                ]
            ],
            resize_keyboard=True,
        )


admin_start = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Рассылка"),
                    KeyboardButton(text="Внести фото"),
                ]  
            ],
            resize_keyboard=True,
        )


admin_menu_but = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Просмотр поста"),
                    KeyboardButton(text="Редактировать"),
                ]  
            ],
            resize_keyboard=True,
        )

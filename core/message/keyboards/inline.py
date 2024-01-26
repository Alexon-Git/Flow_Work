from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.settings import worksheet
from aiogram.utils.keyboard import InlineKeyboardBuilder

# empty_photo = "AgACAgIAAxkBAAPMZUNenWL6L8-YYONWzDLkp7s69kcAAqbOMRszTBhKS3WtHT4Nr7sBAAMCAAN5AAMzBA"

# reviews_btn = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="Посмотреть отзыв", callback_data="to_leave")],
#     [InlineKeyboardButton(text="Оставить отзыв", callback_data="browse")]    
# ])

admin_corect = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать рассылку', callback_data="spam")]  
])

edit_inline_but = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить кнопку", callback_data="add_")
        ],
        [
            InlineKeyboardButton(text="Редакт. кнопку", callback_data="edit_but")
        ],
        [
            InlineKeyboardButton(text="Редакт. фото", callback_data="edit_photo")
        ]
])

# cart_shooze = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="Добавить в корзину", callback_data="order")],
#     [InlineKeyboardButton(text='Назад', callback_data="back")]
# ])

def cart_shooze(row):
    inl_btn_posit =  InlineKeyboardBuilder()
    inl_btn_posit.button(text="Добавить в корзину",callback_data=F"order_{row}")
    inl_btn_posit.button(text='Назад', callback_data="back")
    inl_btn_posit.adjust(1)
    return inl_btn_posit.as_markup() 

def price(brand):# находить все позиции данного бренда
    inl_btn_posit =  InlineKeyboardBuilder()
    price = []
    list = worksheet.get_all_values() # посмотреть как вытаскивать определенные столбцы
    for i in range(len(list)):
        if (list[i][0]==brand) and (list[i][10]=="Есть в наличии"):
            price.append(list[i])
    return price

def inkeb_brand(): # достает все уникальные бренды и добавляет их  кнопки
    brand =  InlineKeyboardBuilder()
    models = worksheet.col_values(1)[2:]
    model_set = sorted(set(models))
    for model in model_set:
        brand.button(text=model,callback_data=model)
    brand.adjust(2)
    return brand.as_markup()

def model(price,st):# достает определенные позиции по модели или размеру
    inl_btn_posit =  InlineKeyboardBuilder()
    posit_i = []
    for i in range(len(price)):
        posit_i.append(price[i][st])
    pst = sorted(set(posit_i))
    for i in range(len(pst)):
        inl_btn_posit.button(text=pst[i],callback_data=pst[i])
    inl_btn_posit.button(text='Назад', callback_data="back")
    inl_btn_posit.adjust(1)
    return inl_btn_posit.as_markup()    

def size(price,st,position):
    inl_btn_posit =  InlineKeyboardBuilder()
    for i in range(len(price)):
        if price[i][st] == position:
            inl_btn_posit.button(text=price[i][st+1],callback_data=price[i][st+1])
    inl_btn_posit.button(text='Назад', callback_data="back")
    inl_btn_posit.adjust(1)
    return inl_btn_posit.as_markup()    

def price_sneaker(price,size,position):
    rate = 0
    for i in range(len(price)):
        if (price[i][2] == position) and (price[i][3] == size):
            rate = price[i][9]      
    return  rate 

def photo_pozish(price,position):
    for i in range(len(price)):
        if price[i][3] == position:
            if price[i][8] == "":
                photo_tovar = "https://startcross.ru/images/logo/logo.png?v=37"
            else:
                photo_tovar = price[i][12]
    return photo_tovar



def sale():
    price = []
    ls = worksheet.get_all_values() 
    list = ls[1:]
    for i in range(len(list[1:])):
        if list[i][7]!="":
            price.append(list[i])
    return price

def sneakers_sale():# достает определенные позиции по модели или размеру
    inl_btn_posit =  InlineKeyboardBuilder()
    sneak_sale = sale()
    for i in range(len(sneak_sale)):
        br = sneak_sale[i][0]
        md = sneak_sale[i][5]
        sz = sneak_sale[i][8]
        inl_btn_posit.button(text=f"{br} {md} {sz}",callback_data=f"{br} {md} {sz}")
    inl_btn_posit.adjust(1)
    return inl_btn_posit.as_markup() 


def photo_sale(position):
    price = sale()
    for i in range(len(price)):
        hh = price[i][0] + " "+ price[i][1] + " "+ price[i][2]
        if hh == position:
            if price[i][8] == "":
                photo_tovar = empty_photo
            else:    
                photo_tovar = price[i][8]
    return photo_tovar

def price_sale(position):
    price = sale()
    for i in range(len(price)):
        hh = price[i][0] + " "+ price[i][1] + " "+ price[i][2]
        if hh == position:
            rate = price[i][7]
    return rate
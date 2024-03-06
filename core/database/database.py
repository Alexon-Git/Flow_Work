import asyncio
from typing import Union
import asyncpg
from asyncpg.exceptions import *

from core.settings import settings

async def connect() -> asyncpg.Connection:
    return await asyncpg.connect(host="localhost",
                                 port="5432",
                                 user=settings.db_user,
                                 password=settings.db_password,
                                 database="orders_aggregator")


########################_SET_DATA_##################################################################
async def set_new_user(user_id: int, username: str):
    """Добавляет пользователя в общую таблицу 'users'"""
    conn = await connect()
    try:
        query = 'INSERT INTO public.users (username, user_id) VALUES ($1, $2)'
        await conn.execute(query, username, user_id)
    finally:
        await conn.close()
    return


async def set_courier(data: dict):
    """Добавляет нового курьера"""
    conn = await connect()
    try:
        query = ('INSERT INTO public.courier (username, user_id, status_payment, date_payment_expiration,'
                 'date_registration, fio, phone, email, city,notification_one,notification_zero,verification) '
                 'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12)')
        await conn.execute(query,
                           data["username"], data["user_id"], data["status_payment"],
                           data["date_payment_expiration"], data["date_registration"], data["fio"],
                           data["phone"], data["email"], data["city"],data["notification_one"],data["notification_zero"],data["verification"])
    finally:
        await conn.close()
    return


async def set_customer(data: dict):
    """Добавляет нового заказчика"""
    conn = await connect()
    try:
        query = ('INSERT INTO public.customer (username, user_id, date_registration, fio, phone, email, city,organization) '
                 'VALUES ($1, $2, $3, $4, $5, $6, $7,$8)')
        await conn.execute(query,
                           data["username"], data["user_id"],
                           data["date_registration"], data["fio"],
                           data["phone"], data["email"], data["city"],data["organization"])
    finally:
        await conn.close()
    return


async def set_request(data: dict):
    """Добавляет новый заказ"""
    conn = await connect()
    try:
        query = ('INSERT INTO public.request (username_customer, user_id_customer, '
                 'date_registration, status_work, adress_a, adress_b, code,price,store_name,message_id,chat_id) '
                 'VALUES ($1, $2, $3, $4, $5, $6, $7,$8,$9,$10,$11)')
        await conn.execute(query,
                           data["username_customer"], data["user_id_customer"],
                           data["date_registration"], data["status_work"],
                           data["adress_a"], data["adress_b"], data["code"],data["price"],data["store_name"],data["message_id"],data["chat_id"])
    finally:
        await conn.close()
    return


# #######################_CHANGE_DATA_################################################################ #
async def payment_courier(user_id: int,date:str) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET status_payment = true,notification_one = false,notification_zero = false, date_payment_expiration = $1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query, date,user_id)
    finally:
        await conn.close()
    return


async def change_notification_one(user_id: int,mode:bool) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET notification_one = $1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query,mode,user_id)
    finally:
        await conn.close()
    return

async def change_notification_zero(user_id: int,mode:bool) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET notification_zero = $1, status_payment = false WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query,mode,user_id)
    finally:
        await conn.close()
    return


async def set_request_courier(id:int,courier_id:int,message_id:int)->None:
    conn = await connect()
    query = 'UPDATE public.request SET courier_id = $1, message_courier_id = $2 WHERE public.request.id = $3'
    try:
        await conn.execute(query, courier_id,message_id, id)
    finally:
        await conn.close()
    return

async def change_status_work(id:int,status:str):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE public.request.id = $2'
    try:
        await conn.execute(query,status,id)
    finally:
        await conn.close()
    return

async def verification_courier(user_id:int,data:str):
    conn = await connect()
    query = 'UPDATE public.courier SET verification = true,date_payment_expiration=$2,notification_one = false,notification_zero = false WHERE public.courier.user_id = $1'
    try:
        await conn.execute(query, user_id,data)
    finally:
        await conn.close()
    return

async def add_score_courier(courier_id:int,point:int):
    conn = await connect()
    query = 'UPDATE public.courier SET point = point+$1, orders = orders+1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query,point, courier_id)
    finally:
        await conn.close()
    return


# #######################_GET_DATA_################################################################ #
async def get_courier(user_id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.courier WHERE public.courier.user_id = $1'
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        return rows[0]
    except IndexError:
        return {}


async def get_user(user_id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.courier WHERE public.courier.user_id = $1'
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        result = {"user_id": rows[0]["user_id"], "username": rows[0]["username"],
                  "status_payment": rows[0]["status_payment"],
                  "date_payment_expiration": rows[0]["date_payment_expiration"],
                  "date_registration": rows[0]["date_registration"],
                  "fio": rows[0]["fio"], "phone": rows[0]["phone"],
                  "email": rows[0]["email"], "city": rows[0]["city"],
                  "notification_one":rows[0]["notification_one"],
                  "notification_zero":rows[0]["notification_zero"]}
    except IndexError:
        return {}
    return result


async def get_customer(user_id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.customer WHERE public.customer.user_id = $1'
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        result = {"user_id": rows[0]["user_id"], "username": rows[0]["username"],
                  "date_registration": rows[0]["date_registration"],
                  "fio": rows[0]["fio"], "phone": rows[0]["phone"],
                  "email": rows[0]["email"], "city": rows[0]["city"],"organization":rows[0]["organization"]}
    except IndexError:
        return {}
    return result


async def get_request(id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.request WHERE public.request.id = $1'
    try:
        rows = await conn.fetch(query, id)
    finally:
        await conn.close()
    try:
        result = {"user_id_customer": rows[0]["user_id_customer"], "username_customer": rows[0]["username_customer"],
                  "date_registration": rows[0]["date_registration"],
                  "status_work": rows[0]["status_work"],
                  "adress_a": rows[0]["adress_a"],
                  "adress_b": rows[0]["adress_b"],
                  "code": rows[0]["code"],"price":rows[0]["price"],
                  "store_name":rows[0]["store_name"],"message_id":rows[0]["message_id"],
                  "chat_id":rows[0]["chat_id"],"courier_id":rows[0]["courier_id"],"message_courier_id":rows[0]["message_courier_id"]}
    except IndexError:
        return {}
    return result


async def get_customer_sent_request(user_id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.request WHERE public.request.user_id_customer = $1'
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        result = []
        for row in rows:
            result.append({"id":row["id"],"user_id_customer": row["user_id_customer"], "username_customer": row["username_customer"],
                    "date_registration": row["date_registration"],
                    "status_work": row["status_work"],
                    "adress_a": row["adress_a"],
                    "adress_b": row["adress_b"],
                    "code": row["code"],"price":row["price"],
                    "store_name":row["store_name"],"message_id":row["message_id"],
                    "chat_id":row["chat_id"], "courier_id":row["courier_id"], "message_courier_id":row["message_courier_id"]})
    except IndexError:
        return {}
    return result

async def get_courier_active_request(user_id: int) -> dict:
    conn = await connect()
    query = "SELECT * FROM public.request WHERE public.request.user_id_customer = $1, public.request.status_work <> 'finish'"
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        result = {"user_id_customer": rows[0]["user_id_customer"], "username_customer": rows[0]["username_customer"],
                  "date_registration": rows[0]["date_registration"],
                  "status_work": rows[0]["status_work"],
                  "adress_a": rows[0]["adress_a"],
                  "adress_b": rows[0]["adress_b"],
                  "code": rows[0]["code"], "price": rows[0]["price"],
                  "store_name": rows[0]["store_name"], "message_id": rows[0]["message_id"],
                  "chat_id": rows[0]["chat_id"], "courier_id": rows[0]["courier_id"],
                  "message_courier_id": rows[0]["message_courier_id"]}
    except IndexError:
        return {}
    return result

async def get_request_id(message_id:int) -> int:
    conn = await connect()
    query = 'SELECT id FROM public.request WHERE public.request.message_id = $1'
    try:
        rows = await conn.fetch(query, message_id)
    finally:
        await conn.close()
    try:
        result = rows[0]["id"]
    except IndexError:
        return 0
    return result

async def get_notification_one(date:str) -> dict:
    conn = await connect()
    query = 'SELECT user_id FROM public.courier WHERE public.courier.date_payment_expiration = $1 AND public.courier.notification_one = false'
    try:
        rows = await conn.fetch(query, date)
    finally:
        await conn.close()
    return rows

async def get_notification_zero(date:str) -> dict:
    conn = await connect()
    query = 'SELECT user_id FROM public.courier WHERE public.courier.date_payment_expiration = $1 AND public.courier.notification_zero = false'
    try:
        rows = await conn.fetch(query, date)
    finally:
        await conn.close()
    return rows


async def get_all_courier() -> list[asyncpg.Record]:
    conn = await connect()
    query = 'SELECT * FROM public.courier'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return rows


async def get_all_customer() -> list[asyncpg.Record]:
    conn = await connect()
    query = 'SELECT * FROM public.customer'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return rows


async def get_id_courier() -> list[int]:
    conn = await connect()
    query = 'SELECT user_id FROM public.courier'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return [i["user_id"] for i in rows]


async def get_id_customer() -> list[int]:
    conn = await connect()
    query = 'SELECT user_id FROM public.customer'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return [i["user_id"] for i in rows]


async def get_id_all_user() -> list[int]:
    conn = await connect()
    query = 'SELECT user_id FROM public.users'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return [i["user_id"] for i in rows]


async def get_all_price() -> list[int]:
    conn = await connect()
    query = 'SELECT price FROM public.request WHERE request.status_work=$1'
    try:
        rows = await conn.fetch(query, "sent")
    finally:
        await conn.close()
    return [i["price"] for i in rows]


# #######################_CHECK_DATA_################################################################ #
async def check_courier(user_id: int) -> bool:
    """Функция проверки регистрации курьера"""
    conn = await connect()
    try:
        result = await conn.fetchval(
            '''
            SELECT EXISTS 
            (
                SELECT user_id FROM public.courier    
                WHERE user_id = $1
            )
            ''', user_id)
    finally:
        await conn.close()
    return result

async def check_number_request_courier(user_id: int) -> bool:
    conn = await connect()
    try:
        result = await conn.fetchval(
            '''
            
                SELECT * FROM public.request    
                WHERE user_id = $1 and status_work <> 'finish'
            ''', user_id)
    finally:
        await conn.close()
    return len(result)>1

async def check_customer(user_id: int) -> bool:
    """Функция проверки регистрации заказчика"""
    conn = await connect()
    try:
        result = await conn.fetchval(
            '''
            SELECT EXISTS 
            (
                SELECT user_id FROM public.customer    
                WHERE user_id = $1
            )
            ''', user_id)
    finally:
        await conn.close()
    return result

async def check_user(user_id: int) -> bool:
    """Функция проверки наличия данных регистрации пользователей"""
    conn = await connect()
    try:
        result = await conn.fetchval(
            '''
            SELECT EXISTS 
            (
                SELECT user_id FROM public.users    
                WHERE user_id = $1
            )
            ''', user_id)
    finally:
        await conn.close()
    return result

async def check_date(date_today:str) -> bool:
    """Функция сравнения дат"""
    conn = await connect()
    try:
        result = await conn.fetchval(
            '''
            SELECT EXISTS 
            (
                SELECT user_id FROM public.users    
                WHERE user_id = $1
            )
            ''', date_today)
    finally:
        await conn.close()
    return result


# ####################################################################################################
async def save_new_admin(user_id: int):
    conn = await connect()
    query = 'UPDATE public.users SET admin = true WHERE public.users.user_id = $1'
    try:
        await conn.execute(query, user_id)
    finally:
        await conn.close()
    return


async def get_id_admin() -> list[int]:
    conn = await connect()
    query = 'SELECT user_id FROM public.users WHERE public.users.admin = true'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    admins = [i["user_id"] for i in rows]
    admins.append(settings.bots.admin_id)
    return admins


async def get_data_admin() -> list[asyncpg.Record]:
    conn = await connect()
    query = 'SELECT * FROM public.users WHERE public.users.admin = true'
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    return rows


async def deleted_admin(user_id: int):
    conn = await connect()
    query = 'UPDATE public.users SET admin = false WHERE public.users.user_id = $1'
    try:
        await conn.execute(query, user_id)
    finally:
        await conn.close()
    return


async def deleted_customer(user_id: int):
    conn = await connect()
    query = 'DELETE FROM public.customer WHERE public.customer.user_id = $1'
    try:
        await conn.execute(query, user_id)
    finally:
        await conn.close()
    return


async def deleted_courier(user_id: int):
    conn = await connect()
    query = 'DELETE FROM public.courier WHERE public.courier.user_id = $1'
    try:
        await conn.execute(query, user_id)
    finally:
        await conn.close()
    return


async def update_courier(data: dict):
    conn = await connect()
    query = ('UPDATE public.courier SET fio=$1, phone=$2, email=$3, city=$4 '
             'WHERE public.courier.user_id=$5')
    try:
        await conn.execute(query, data["fio"], data["phone"], data["email"], data["city"], data["user_id"])
    finally:
        await conn.close()
    return


async def update_customer(data: dict):
    conn = await connect()
    query = ('UPDATE public.courier SET fio=$1, phone=$2, email=$3, city=$4, organization=$5 '
             'WHERE public.courier.user_id=$6')
    try:
        await conn.execute(query, data["fio"], data["phone"], data["email"], data["city"], data["organization"], data["user_id"])
    finally:
        await conn.close()
    return



import asyncio
from typing import Union

import asyncpg
from asyncpg.exceptions import *

user = "postgres"
password = "12345"


async def connect() -> asyncpg.Connection:
    return await asyncpg.connect(host="localhost",
                                 port="5433",
                                 user=user,
                                 password=password,
                                 database="order_aggregator")


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
                 'date_registration, fio, phone, email, city,notification_one,notification_zero) '
                 'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)')
        await conn.execute(query,
                           data["username"], data["user_id"], data["status_payment"],
                           data["date_payment_expiration"], data["date_registration"], data["fio"],
                           data["phone"], data["email"], data["city"],data["notification_one"],data["notification_zero"])
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


async def set_request(user_id, data: dict):
    """Добавляет новый заказ"""
    conn = await connect()
    try:
        query = ('INSERT INTO public.courier (username_customer, user_id_customer, '
                 'date_registration, status_work, adress_a, adress_b, code) '
                 'VALUES ($1, $2, $3, $4, $5, $6, $7)')
        await conn.execute(query, user_id,
                           data["username_customer"], data["user_id_customer"],
                           data["date_registration"], data["status_work"],
                           data["adress_a"], data["adress_b"], data["code"])
    finally:
        await conn.close()
    return


# #######################_CHANGE_DATA_################################################################ #
async def payment_courier(user_id: int,date:str) -> dict:
    conn = await connect()
    query = ('UPDATE public.courier SET status_payment = true,notification_one = false,notification_zero = false,'
             ' date_payment_expiration = $1 WHERE public.courier.user_id = $2')
    try:
        await conn.execute(query, date, user_id)
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
    query = 'UPDATE public.courier SET notification_zero = $1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query,mode,user_id)
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


async def get_request(user_id: int) -> dict:
    conn = await connect()
    query = 'SELECT * FROM public.request WHERE public.request.user_id = $1'
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
                  "code": rows[0]["code"]}
    except IndexError:
        return {}
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

#   ПРоверка наличия айди в БД
async def main():
    root = await get_courier(123560344)
    print(root)
    return


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from typing import Union
import asyncpg
import datetime
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
                           data["phone"], data["email"], data["city"], data["notification_one"],
                           data["notification_zero"], data["verification"])
    finally:
        await conn.close()
    return


async def set_customer(data: dict):
    """Добавляет нового заказчика"""
    conn = await connect()
    try:
        query = (
            'INSERT INTO public.customer (username, user_id, date_registration, fio, phone, email, city,organization) '
            'VALUES ($1, $2, $3, $4, $5, $6, $7,$8)')
        await conn.execute(query,
                           data["username"], data["user_id"],
                           data["date_registration"], data["fio"],
                           data["phone"], data["email"], data["city"], data["organization"])
    finally:
        await conn.close()
    return


async def check_order_in_base(number):
    conn = await connect()
    try:
        query = 'SELECT * FROM public.request WHERE code = $1'
        await conn.execute(query, number)
    except:
        return True
    else:
        return False


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
                           data["adress_a"], data["adress_b"], data["code"], data["price"], data["store_name"],
                           data["message_id"], data["chat_id"])
    finally:
        await conn.close()
    return


# #######################_CHANGE_DATA_################################################################ #
async def payment_courier(user_id: int, date: str) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET status_payment = true,notification_one = false,notification_zero = false, date_payment_expiration = $1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query, date, user_id)
    finally:
        await conn.close()
    return


async def change_notification_one(user_id: int, mode: bool) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET notification_one = $1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query, mode, user_id)
    finally:
        await conn.close()
    return


async def change_notification_zero(user_id: int, mode: bool) -> dict:
    conn = await connect()
    query = 'UPDATE public.courier SET notification_zero = $1, status_payment = false WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query, mode, user_id)
    finally:
        await conn.close()
    return


async def set_request_courier(id: int, courier_id: int, message_id: int) -> None:
    conn = await connect()
    query = 'UPDATE public.request SET courier_id = $1, message_courier_id = $2 WHERE public.request.id = $3'
    try:
        await conn.execute(query, courier_id, message_id, id)
    finally:
        await conn.close()
    return


async def change_status_work(id: int, status: str):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE public.request.id = $2'
    try:
        await conn.execute(query, status, id)
    finally:
        await conn.close()
    return


async def verification_courier(user_id: int, data: str):
    conn = await connect()
    query = 'UPDATE public.courier SET verification = true,date_payment_expiration=$2,notification_one = false,notification_zero = false WHERE public.courier.user_id = $1'
    try:
        await conn.execute(query, user_id, data)
    finally:
        await conn.close()
    return


async def add_score_courier(courier_id: int, point: int):
    conn = await connect()
    query = 'UPDATE public.courier SET point = point+$1, orders = orders+1 WHERE public.courier.user_id = $2'
    try:
        await conn.execute(query, point, courier_id)
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
                  "notification_one": rows[0]["notification_one"],
                  "notification_zero": rows[0]["notification_zero"]}
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
                  "email": rows[0]["email"], "city": rows[0]["city"], "organization": rows[0]["organization"]}
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
                  "code": rows[0]["code"], "price": rows[0]["price"],
                  "store_name": rows[0]["store_name"], "message_id": rows[0]["message_id"],
                  "chat_id": rows[0]["chat_id"], "courier_id": rows[0]["courier_id"],
                  "message_courier_id": rows[0]["message_courier_id"]}
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
            result.append({"id": row["id"], "user_id_customer": row["user_id_customer"],
                           "username_customer": row["username_customer"],
                           "date_registration": row["date_registration"],
                           "status_work": row["status_work"],
                           "adress_a": row["adress_a"],
                           "adress_b": row["adress_b"],
                           "code": row["code"], "price": row["price"],
                           "store_name": row["store_name"], "message_id": row["message_id"],
                           "chat_id": row["chat_id"], "courier_id": row["courier_id"],
                           "message_courier_id": row["message_courier_id"]})
    except IndexError:
        return {}
    return result

async def request_work_into_db(code, courier_id: int):
    conn = await connect()
    query1 = 'UPDATE public.request SET status_work = $1 WHERE code = $2'
    query2 = 'UPDATE public.request SET courier_id = $1 WHERE code = $2'
    status = 'work'
    try:
        await conn.execute(query1, status,code)
        await conn.execute(query2, courier_id,code)
    finally:
        await conn.close()
    return

async def request_work_close_db(code):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE code = $2'
    query1 = 'UPDATE public.request SET courier_id = $1 WHERE code = $2'
    n = None
    status = 'sent'
    try:
        await conn.execute(query, status, code)
        await conn.execute(query1, n, code)
    finally:
        await conn.close()
    return

async def request_work_finish_db(code):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE code = $2'
    status = 'finish'
    try:
        await conn.execute(query, status, code)
    finally:
        await conn.close()
    return

async def admin_request_active(code):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE code = $2'
    status = 'sent'
    try:
        await conn.execute(query, status, code)
    finally:
        await conn.close()
    return

async def admin_request_close(code):
    conn = await connect()
    query = 'UPDATE public.request SET status_work = $1 WHERE code = $2'
    status = 'finish'
    try:
        await conn.execute(query, status, code)
    finally:
        await conn.close()
    return

async def check_finish(code):
    conn = await connect()
    query = 'SELECT status_work FROM public.request WHERE code = $1'
    try:
        status = await conn.fetchval(query, code)
    finally:
        await conn.close()
    return status


async def check_courier_request(courier):
    conn = await connect()
    query = "SELECT code FROM public.request WHERE courier_id = $1 AND status_work <> 'finish'"
    try:
        code = await conn.fetchval(query, courier)
    finally:
        await conn.close()
    return code

async def get_courier_id_for_code(code):
    conn = await connect()
    query = "SELECT courier_id FROM public.request WHERE code = $1"
    try:
        code = await conn.fetchval(query, code)
    finally:
        await conn.close()
    return code

async def new_courier_request(code, courier_id):
    conn = await connect()
    query = "UPDATE public.request SET courier_id = $1, status = 'work' WHERE code = $2"
    try:
        code = await conn.execute(query, courier_id, code)
    finally:
        await conn.close()
    return

async def request_status_get_order(code):
    conn = await connect()
    try:
        query = "UPDATE public.request SET status_work = 'get_order' WHERE code = $1"
        await conn.execute(query, code)
    finally:
        await conn.close()
    return

async def request_update_money(code, money: int):
    conn = await connect()
    try:
        query = "UPDATE public.request SET price = $1 WHERE code = $2"
        await conn.execute(query, money, code)
    finally:
        await conn.close()
    return

async def request_status_shop(code):
    conn = await connect()
    try:
        query = "UPDATE public.request SET status_work = 'shop' WHERE code = $1"
        await conn.execute(query, code)
    finally:
        await conn.close()
    return

async def request_status_arrived(code):
    conn = await connect()
    try:
        query = "UPDATE public.request SET status_work = 'arrived' WHERE code = $1"
        await conn.execute(query, code)
    finally:
        await conn.close()
    return


async def get_courier_active_request(user_id: int) -> dict:
    conn = await connect()
    query = "SELECT * FROM public.request WHERE (public.request.status_work = 'sent' OR courier_id = $1) AND (public.request.status_work <> 'finish') ORDER BY status_work = 'sent' DESC;"
    try:
        rows = await conn.fetch(query, user_id)
    finally:
        await conn.close()
    try:
        result = {}
        for i in range(len(rows)):
            result.update({f"user_id_customer_{i}": rows[i]["user_id_customer"], f"username_customer_{i}": rows[i]["username_customer"],
                      f"date_registration_{i}": rows[i]["date_registration"],
                      f"status_work_{i}": rows[i]["status_work"],
                      f"adress_a_{i}": rows[i]["adress_a"],
                      f"adress_b_{i}": rows[i]["adress_b"],
                      f"code_{i}": rows[i]["code"], f"price_{i}": rows[i]["price"],
                      f"store_name_{i}": rows[i]["store_name"], f"message_id_{i}": rows[i]["message_id"],
                      f"chat_id_{i}": rows[i]["chat_id"], f"courier_id_{i}": rows[i]["courier_id"],
                      f"message_courier_id_{i}": rows[i]["message_courier_id"]})
    except IndexError:
        return None
    return result



async def new_place_a(code, new_place):
    conn = await connect()
    query = 'UPDATE public.request SET adress_a = $1 WHERE code = $2'
    try:
        await conn.execute(query, new_place, code)
    finally:
        await conn.close()
    return

async def new_place_b(code, new_place):
    conn = await connect()
    query = 'UPDATE public.request SET adress_b = $1 WHERE code = $2'
    try:
        await conn.execute(query, new_place, code)
    finally:
        await conn.close()
    return



async def pinned_orders_request() -> dict:
    conn = await connect()
    query = "SELECT * FROM public.request WHERE status_work <> 'finish' AND status_work <> 'sent'"
    try:
        rows = await conn.fetch(query)
    finally:
        await conn.close()
    try:
        result = {}
        for i in range(len(rows)):
            result.update({f"user_id_customer_{i}": rows[i]["user_id_customer"], f"username_customer_{i}": rows[i]["username_customer"],
                      f"date_registration_{i}": rows[i]["date_registration"],
                      f"status_work_{i}": rows[i]["status_work"],
                      f"adress_a_{i}": rows[i]["adress_a"],
                      f"adress_b_{i}": rows[i]["adress_b"],
                      f"code_{i}": rows[i]["code"], f"price_{i}": rows[i]["price"],
                      f"store_name_{i}": rows[i]["store_name"], f"message_id_{i}": rows[i]["message_id"],
                      f"chat_id_{i}": rows[i]["chat_id"], f"courier_id_{i}": rows[i]["courier_id"],
                      f"message_courier_id_{i}": rows[i]["message_courier_id"]})
    except IndexError:
        return None
    return result


async def get_request_id(message_id: int) -> int:
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


async def get_notification_one(date: str) -> dict:
    conn = await connect()
    query = 'SELECT user_id FROM public.courier WHERE public.courier.date_payment_expiration = $1 AND public.courier.notification_one = false'
    try:
        rows = await conn.fetch(query, date)
    finally:
        await conn.close()
    return rows


async def get_notification_zero(date: str) -> dict:
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
        result = await conn.fetch(
            '''
            
                SELECT * FROM request  
                WHERE courier_id = $1 and status_work <> 'finish'
            ''', user_id)
    finally:
        await conn.close()
    return len(result) > 1


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


async def check_date(date_today: str) -> bool:
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
        await conn.execute(query, data["fio"], data["phone"], data["email"], data["city"], data["organization"],
                           data["user_id"])
    finally:
        await conn.close()
    return

################ WORK WITH APPLICATION ########################


async def into_in_orders(courier_id: int, cod):
    conn = await connect()
    try:
        await conn.execute(f'INSERT INTO flow(courier, orders_id), VALUES($1, $2)', courier_id, cod)
    finally:
        await conn.close()
    return



async def check_courier_1(cod):
    conn = await connect()
    try:
        result = await conn.fetchval(f'SELECT courier FROM flow WHERE order_id=$1', cod)
    finally:
        await conn.close()
    return result


async def refuse_db(cod):
    conn = await connect()
    try:
        await conn.execute(f'DELETE FROM flow WHERE order_id=$1', cod)
        return True
    finally:
        await conn.close()
    return

async def arrived_to_shop_db(courier_id:int):
    conn = await connect()
    now = datetime.datetime.now()
    status = 'shop'
    st = ''
    try:
        await conn.execute(f'UPDATE flow SET status=$1 WHERE courier=$2 AND status <> "close"', status, courier_id, )
        await conn.execute(f'UPDATE flow SET time_shop=$1 WHERE courier=$2 AND status <> "close"', now,courier_id)
    finally:
        await conn.close()

async def arrived_to_shop_db_admin(cod):
    conn = await connect()
    now = datetime.datetime.now()
    status = 'shop'
    try:
        await conn.execute(f'UPDATE flow SET status=$1 WHERE order_id=$2', status,cod)
        await conn.execute(f'UPDATE flow SET time_shop=$1 WHERE order_id=$2', now,cod)
    finally:
        await conn.close()
    return
async def get_order_db(courier_id:int):
    conn = await connect()
    status = 'get_order'
    try:
        await conn.execute(f'UPDATE flow SET status=$1 WHERE courier=$2 AND status <> "close"', status,courier_id)
    finally:
        await conn.close()
    return

async def get_order_db_admin(cod):
    conn = await connect()
    status = 'get_order'
    try:
        await conn.execute(f'UPDATE flow SET status=$1 WHERE order_id=$2', status, cod)
    finally:
        await conn.close()
    return

async def arrived_to_place_db(courier:int):
    conn = await connect()
    now = datetime.datetime.now()
    status = "arrived"
    try:
        await conn.execute(f'UPDATE public.flow SET time_place=$1, status=$2 WHERE courier=$3 AND status <> "close"', now, status, courier)
    finally:
        await conn.close()
    return

async def arrived_to_place_db_admin(cod):
    conn = await connect()
    now = datetime.datetime.now()
    try:
        await conn.execute(f'UPDATE public.flow SET time_place=$1, status="arrived" WHERE order_id=$2', now, cod)
    finally:
        await conn.close()
    return
async def close_order_db(courier:int):
    conn = await connect()
    try:
        await conn.execute(f'UPDATE public.flow SET status="close" WHERE courier=$1', courier)
    finally:
        await conn.close()
    return


async def close_order_db_admin(cod):
    conn = await connect()
    try:
        await conn.execute(f'UPDATE public.flow SET status="close" WHERE orders_id=$1', cod)
    finally:
        await conn.close()
    return


async def active_order_db_admin(cod):
    conn = await connect()
    try:
        await conn.execute(f'UPDATE public.flow SET status=NULL WHERE orders_id=$1', cod)
    finally:
        await conn.close()
    return


async def new_courier_db(cod, courier_id:int):
    conn = await connect()
    try:
        await conn.execute(f'UPDATE public.flow SET courier=$1 WHERE orders_id=$2', courier_id, cod)
    finally:
        await conn.close()
    return




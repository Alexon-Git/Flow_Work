import asyncio

import requests as requests
import aioschedule
from core.database.database import check_order_in_base, set_request

api = '74be8e38f2fbe35f073d6c24529b4f45'


# 9
async def request_store():
    requ = requests.post(url='https://rosenta.ru/api/v1/orders/get_list', data={'secret_key': api,
                                                                                'per_page': 1})
    order_num = requ.json()['data'][0]['order_num']['value']
    status_id = requ.json()['data'][0]['order_status_id']['value']
    if status_id == '9':
        if check_order_in_base(order_num):
            data = {"username_customer": requ.json()['data'][0]['order_person']['value'],
                    "user_id_customer": requ.json()['data'][0]['sites_client_id']['value'],
                    "date_registration": requ.json()['data'][0]['created_at']['value'],
                    "status_work": 'Доставка', "code": order_num,
                    'adress_a': '-', 'adress_b': '-', 'price': '-', 'store_name': '-', 'message_id': '-',
                    'chat_id': '-', 'courier_id': '', 'message_courier_id': '-'}
            await set_request(data)


async def check_order_store():
    aioschedule.every().minute.do(request_store)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

import os
import json
from core.settings import home


def set_city_stat(fild: str, city: int):
    if not os.path.exists(f"{home}/statistics/data/{city}.json"):
        with open(f"{home}/statistics/data/{city}.json", "w") as f:
            data = {
                "record_new": 0,
                "record_cancel": 0,
                "record_done": 0
            }
            data[fild] += 1
            json.dump(data, f)
        return
    with open(f"{home}/statistics/data/{city}.json", "w+") as f:
        data = json.load(f)
        data[fild] += 1
        json.dump(data, f)


def get_statistic(city_id: int) -> dict:
    with open(f"{home}/statistics/data/{city_id}.json", "r") as f:
        data = json.load(f)
    return data


def clean_statistic(chat_id: int):
    with open(f"{home}/statistics/data/{chat_id}.json", "w") as f:
        data = {
            "record_new": 0,
            "record_cancel": 0,
            "record_done": 0
        }
        json.dump(data, f)


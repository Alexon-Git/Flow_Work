from core.settings import home


def get_text_start_mess() -> str:
    with open(f"{home}/message/start_mess.txt", "r", encoding="utf-8")as f:
        return f"{f.read()}"


def set_text_start_mess(new_text: str):
    with open(f"{home}/message/start_mess.txt", "w", encoding="utf-8")as f:
        f.write(new_text)


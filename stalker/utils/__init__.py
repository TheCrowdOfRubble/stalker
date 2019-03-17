import requests


def get_random_proxy():
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')


def get_id_and_name(url: str):
    user_id = 0
    username = ""
    if url.startswith("https://weibo.cn/u/"):
        user_id = int(url[19:])
    else:
        username = url[17:]
    return user_id, username

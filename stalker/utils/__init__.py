import requests


def get_random_proxy():
    return "http://" + requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')

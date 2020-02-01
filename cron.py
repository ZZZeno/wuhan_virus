import requests


def get_data():
    requests.get('http://127.0.0.1:20201/api/scheduler')
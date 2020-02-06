import requests
import json
import matplotlib.pyplot as plt

def get_page(retries=3) -> requests.get:
    while retries > 0:
        try:
            response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia', timeout=60)
            response.encoding = 'utf-8'
            return response
        except:
            retries -= 1
            return None


def wrap_response(status, msg="", data=""):
    if status == "fail":
        code = 1
    else:
        code = 0
    return json.dumps({"code": code, "message": msg, "data": data})

# main()

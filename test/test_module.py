
import requests


def work_test(self):
        URL = "http://api.noti.daumkakao.io/send/group/kakaotalk"
        params = {"from": "watchtower.bot", "to": 11859, "msg": "test_message", "ps": False}
        res = requests.get(URL, params=params)
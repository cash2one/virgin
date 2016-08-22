# coding=utf-8
import datetime
import requests
from connect import conn
from bson import ObjectId, json_util
import json
import random
SMSnetgate = 'http://125.211.222.237:10031'
def send_sms():
    data = {'sign': '美食地图',
            'tpl': 'SMS_8161119',
            'param': json.dumps({"code": str(random.randint(1000000, 9999999))[1:]}),
            'tel': '18746428128',
            'ex': '#foodmap.mobile'
            }
    req = requests.post(SMSnetgate + '/sms.send', data)
    return req.json()
    pass
if __name__ == '__main__':
    send_sms()
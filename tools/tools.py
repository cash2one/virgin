#--coding:utf-8--#
_author_='hcy'
from bson import json_util

def return_json(code,message,data):
    json={
        "code":code,
        "message":message,
        "data": data
    }
    return json
#--coding:utf-8--#
import json

_author_='hcy'
from bson import json_util, ObjectId


def return_json(code,message,data):
    json={
        "code":code,
        "message":message,
        "data": data
    }
    return json

ff = {'status': 'int',
      'type': 'int',
      'restaurant_id': 'obj'
      }

def orderformate(pdict={}):
    pdict = dict(filter(lambda x:x[1]!='', pdict.items()))
    data = formatp(pdict)
    return data
    pass

def formatp(data):
    for key in data.keys():
        data[key]=format_type(data[key], ff[key])
    return data

def format_type(data, type):
    if type == 'str':
        return str(data)
    elif type == 'int':
        return int(data)
    elif type == 'obj':
        return ObjectId(data)
    pass
def json_value(json_data, key_name, dump=False):
    if json_data is None:
        return None
    if key_name in json_data.keys():
        if dump:
            return json.dumps(json_data[key_name])
        else:
            return json_data[key_name]
    else:
        return None
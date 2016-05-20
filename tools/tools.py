#--coding:utf-8--#
import json


from connect import conn
from bson import ObjectId,json_util
mongo=conn.mongo_conn()

def return_json(code,message,jwt,data):
    if jwt:
        data = data
    else:
        data = {"jwt":"field"}
    json={
        "code":code,
        "message":message,
        "auto":jwt,
        "data": data
    }
    return json


def orderformate(pdict={},table={}):
    pdict = dict(filter(lambda x:x[1]!='', pdict.items()))
    data = formatp(pdict,table)
    return data
    pass

def formatp(data,table):
    for key in data.keys():
        data[key]=format_type(data[key], table[key])
    return data

def format_type(data, type):
    if type == 'str':
        return str(data)
    elif type == 'int':
        return int(data)
    elif type == 'obj':
        return ObjectId(data)
    elif type == 'boo':
        return bool(data)
    elif type == 'flo':
        return float(data)
    else:
        return data
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

class Foormat:
    def __init__(self, objid):
        self.objid = {"_id": ObjectId(objid)}
        self.data = self.__get_db_data()
        self.dish_data = None
        self.menu_data = None
        self.new_menu = None

    def rebuild(self):
        if self.new_menu is None:
            rebuild_data = self.data
        else:
            rebuild_data = self.new_menu
        menu_list = []
        for menu in rebuild_data['menu']:
            new_menu = dict()
            for key in menu.keys():
                if key == 'dishs':
                    dishs = []
                    for dish in menu['dishs']:
                        if 'id' in dish.keys():
                            if dish['id'] in self.dish_data.keys():
                                dish_new = {}
                                for key_name in dish.keys():
                                    if key_name in self.dish_data[dish['id']].keys():
                                        dish_new[key_name] = self.dish_data[dish['id']][key_name]
                                    else:
                                        dish_new[key_name] = dish[key_name]
                                dishs.append(dish_new)
                            else:
                                dishs.append(dish)
                        else:
                            dishs.append(dish)
                    new_menu['dishs'] = dishs
                else:
                    if self.menu_data is not None and (menu['id'] in self.menu_data.keys()):
                        if key in self.menu_data[menu['id']].keys():
                            new_menu[key] = self.menu_data[menu['id']][key]
                        else:
                            new_menu[key] = menu[key]
                    else:
                        new_menu[key] = menu[key]
            menu_list.append(new_menu)
        self.new_menu = {'menu': menu_list}
        return True

    def re_dish(self, dish_data=None):
        self.dish_data = dish_data

    def re_menu(self, menu_data=None):
        self.menu_data = menu_data

    def __get_db_data(self):
        return mongo.restaurant.find(self.objid, {"menu": 1})[0]

    def submit2db(self):
        if self.new_menu is None:
            self.rebuild()
        try:
            mongo.restaurant.update_one(self.objid, {"$set": self.new_menu})
            return True
        except Exception, e:
            return False


if __name__ == '__main__':
    dish = {
                    "is_enabled" : 'str',
                    "name" : "str",
                    "shijia" : 'boo',
                    "price" : 'flo',
                    "is_recommend" : 'boo',
                    "discount_price" : 'flo',
                    "summary" : "str",
                    "praise_num" : 'int',
                    "guide_image" : "str",
                    "type" : "str",
                    "id" : "str"
            }
    obj = '57327f4a8831ac0e5cb96404'
    test_dish = {
        '201605111118535612': {'discount_price': 66,'name': '111111111111111111111111111111111111111111111111'}, '201605111003381987': {'discount_price': 88}
    }
    test_menu = {
        '201605111118535612': {'name': '111111111111111111111111111111111111111111111111'}
    }
    test_data = mongo.restaurant.find({"_id" : ObjectId("57327f4a8831ac0e5cb96404")},{"menu":1})[0]
    # print json_util.dumps(test_data,ensure_ascii=False,indent=2)
    first = Foormat(obj)
    first.re_dish(test_dish)
    first.re_menu(test_menu)
    print first.submit2db()

    pass
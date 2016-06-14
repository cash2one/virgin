# coding=utf-8
import json
import os

import datetime
import random

from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler
import urllib2
import re
from flask import request, Response

import connect
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


class Restaurant:
    def __init__(self, ident_json):
        self.ident = ident_json
        self.data, self.obj_id = self.__find_item()
        self.dish_data = None
        self.menu_data = None
        self.info_data = None
        self.add_dish_data = None
        self.new_menu = None

    def __find_item(self):
        if '_id' in self.ident:
            f = {"_id": ObjectId(self.ident['_id'])}
        elif 'menu_id' in self.ident:
            f = {"menu.id": self.ident['menu_id']}
        elif 'dish_id' in self.ident:
            f = {"menu.dishs.id": self.ident['dish_id']}
        elif 'admin_id' in self.ident:
            f = {"user": {"$in": [ObjectId(self.ident['admin_id'])]}}
        else:
            return None, ''
        found = json_util.loads(json_util.dumps(mongo.restaurant.find_one(f)))
        return found, '' if found is None else str(found['_id'])

    def info(self, key=None):
        if self.data is None:
            # print 'Noting in db'
            return None
        need = None
        if '_id' in self.ident:
            need = self.data
        elif 'menu_id' in self.ident:
            for menu in self.data['menu']:
                if menu['id'] == self.ident['menu_id']:
                    need = menu
        elif 'dish_id' in self.ident:
            for menu in self.data['menu']:
                if menu['dish_type'] == '1':
                    for dish in menu['dishs']:
                        if str(dish['id']) == str(self.ident['dish_id']):
                            need = dish
        else:
            print 'Not Support input ident'
            need = None
        if key:
            if need:
                return need[key]
            else:
                return None
        else:
            return need

    def get_item(self, key_name):
        if self.data is None:
            print 'Data ERROR'
            return None
        else:
            if key_name == '_id':
                return self.obj_id
            elif key_name in self.data.keys():
                return self.data[key_name]
            else:
                'KeyName Error'
                return None

    def add_dish(self, dish_data=None):
        self.add_dish_data = dish_data

    def re_dish(self, dish_data=None):
        self.dish_data = dish_data

    def re_menu(self, menu_data=None):
        self.menu_data = menu_data

    def re_infos(self, info_data=None):
        self.info_data = info_data

    def rebuild(self):
        if self.new_menu is None:
            rebuild_data = self.data
        else:
            rebuild_data = self.new_menu
        menu_list = []
        for menu in rebuild_data['menu']:  # 循环数据库的菜单
            new_menu = dict()
            for key in menu.keys():  # 循环菜单的键名
                if key == 'dishs':  # 如果是菜品列表
                    dishs = []
                    for dish in menu['dishs']:  # 循环菜单中的菜品
                        try:
                            if dish['id'] in self.dish_data.keys():  # 判断是否是需要修改的菜品
                                dish_new = {}
                                for key_name in dish.keys():  # 循环菜品包含的键名
                                    if key_name in self.dish_data[dish['id']].keys():  # 如果是需要修改的键
                                        dish_new[key_name] = self.dish_data[dish['id']][key_name]
                                    else:  # 如果不需要修改
                                        dish_new[key_name] = dish[key_name]
                                dishs.append(dish_new)
                            else:  # 不是要修改的菜品
                                dishs.append(dish)
                        except Exception, e:
                            print e
                            dishs.append(dish)
                    if self.add_dish_data:
                        if menu['id'] in self.add_dish_data.keys():  # 如果当前菜单是需要添加菜品的菜单
                            for new_dish in self.add_dish_data[menu['id']]:  # 循环操作添加新菜品
                                dishs.append(new_dish)
                    new_menu['dishs'] = dishs
                else:  # 如果是菜单信息
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

    def submit2db(self):
        if self.new_menu is None:
            self.rebuild()
        try:
            update = self.info_data
            if self.new_menu:
                update['menu'] = self.new_menu['menu']
            mongo.restaurant.update_one({"_id": ObjectId(self.obj_id)},
                                        {"$set": update})
            return True
        except Exception, e:
            print e
            return False


class Discount:
    def __init__(self, objid):
        self.objid = {"_id": ObjectId(objid)}
        self.data = self.__get_db_data()
        self.dish_data = None
        self.menu_data = None
        self.new_menu = None
        self.add_dish_data = None
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
                    if menu['name'] !='优惠菜' and menu['name'] !='推荐菜' and menu['dish_type'] =='1' and menu['dishs']!=[]:
                        for dish in menu['dishs']:
                            try:
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
                            except Exception, e:
                                dishs.append(dish)
                                pass
                        if self.add_dish_data:
                            if menu['id'] in self.add_dish_data.keys():  # 如果当前菜单是需要添加菜品的菜单
                                for new_dish in self.add_dish_data[menu['id']]:  # 循环操作添加新菜品
                                    dishs.append(new_dish)
                        new_menu['dishs'] = dishs
                    else:
                        new_menu[key] = menu[key]
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
    def add_dish(self, dish_data=None):
        self.add_dish_data = dish_data
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
def pimg(uu):
  # try:
    #创建一个请求
    handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler]
    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)
    # 打开图片
    cc = open(uu, "rb")
    datagen, headers = multipart_encode({"image": cc })
    #发送请求
    request = urllib2.Request(connect.conn.imageIP , datagen, headers)
    #获取返回中的内容
    re1 = r"<h1>MD5:(?P<md5>.*?)</h1>"
    match5 = re.findall(re1,urllib2.urlopen(request).read())
    a = match5[0]
    cc.close()
    print str(a).replace(" ","")
    return str(a).replace(" ","")
  # except Exception, e:
  #       return e


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))
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
    obj = '57329b1f0c1d9b2f4c85f8e3'
    test_dish = {
        '201605111118535612': {'discount_price': 66,'name': '111111111111111111111111111111111111111111111111'}, '201605111003381987': {'discount_price': 88}
    }
    test_menu = {
        '201605111118535612': {'name': '111111111111111111111111111111111111111111111111'}
    }
    test_add = {
        '201605111038236629': [{
                    "is_enabled" : True,
                    "name" : "1981肥牛王",
                    "shijia" : False,
                    "price" : 12.0,
                    "is_recommend" : True,
                    "danwei" : "",
                    "discount_price" : 55555555555.0,
                    "summary" : "",
                    "praise_num" : 0,
                    "guide_image" : "",
                    "type" : "0",
                    "id" : "201605111041429997"
                }]
    }
    # test_data = mongo.restaurant.find({"_id" : ObjectId("57327f4a8831ac0e5cb96404")},{"menu":1})[0]
    # print json_util.dumps(test_data,ensure_ascii=False,indent=2)
    # first = Foormat(obj)
    # first.add_dish(test_add)
    # first.re_dish(test_dish)
    # first.re_menu(test_menu)
    # print first.submit2db()
    print Restaurant({'dish_id': '201605111053268902'}).info
    pass

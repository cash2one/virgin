#--coding:utf-8--#
import pymongo
from flask import request
import datetime
_author_='hcy'
from connect import conn
from bson import ObjectId,json_util
import time
mongo=conn.mongo_conn()

def getroomslist(restaurant_id, preset_time):
    start=datetime.datetime(*time.strptime(preset_time,'%Y-%m-%d')[:6])
    end = datetime.datetime(*time.strptime(preset_time,'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
    rooms=mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"rooms":1})
    a=json_util.loads(json_util.dumps(rooms))
    b = a["rooms"]
    type_list=[]
    for i in b:
        if i["room_people_name"] not in type_list:
            if i["room_people_name"] == '大厅':
                type_list.insert(0, i["room_people_name"])
            else:
                type_list.append(i["room_people_name"])
    data = {}
    list=[]
    for a in type_list:
        room={}
        room["room_people_num"]=a
        rooms=[]
        for i1 in b:
            if i1["room_people_name"]==a:
                item={}
                item["room_id"]=i1["room_id"]
                item["room_name"]=i1["room_name"]
                pdict = {'room_id':i1['room_id'],'status':3,'preset_time': {'$gte': start, '$lt': end}}
                orderbyroom = mongo.order.find(pdict).sort('add_time', pymongo.DESCENDING)
                orderlist = []

                for order in orderbyroom:
                    orderdict = {}
                    for inorder in order.keys():
                        if inorder == '_id':
                            orderdict['id'] = str(order[inorder])
                        elif inorder == 'preset_time':
                            orderdict['preset_time'] = order[inorder].strftime('%H:%M')
                        elif inorder == 'numpeople':
                            orderdict['numpeople'] = int(order[inorder])
                    orderlist.append(orderdict)
                item['orderinfo'] = orderlist
                rooms.append(item)

        room["room_count"]=rooms
        list.append(room)
    data['list'] = list
    # print list
    return data

def getroomorderlist(restaurant_id,preset_time):
    rooms=mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"rooms":1})
    start=datetime.datetime(*time.strptime(preset_time,'%Y-%m-%d')[:6])
    end = datetime.datetime(*time.strptime(preset_time,'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
    data=[]
    for i in rooms['rooms']:
        json = {}
        for key in i.keys():
            if key == 'room_id':
                json['room_id'] = str(i[key])
            elif key == 'room_name':
                json['room_name'] = i[key]
        #此处查询order表 条件是：i['room_id']和preset_time区间
        pdict = {'room_id':i['room_id'],'preset_time': {'$gte': start, '$lt': end}}
        orderbyroom = mongo.order.find(pdict)
        orderdict = {}
        orderlist = []
        for order in orderbyroom:
            for inorder in order.keys():
                if inorder == '_id':
                    orderdict['id'] = str(order[inorder])
                elif inorder == 'preset_time':
                    orderdict['preset_time'] = order[inorder].strftime('%H:%M')
                elif inorder == 'numpeople':
                    orderdict['preset_time'] = int(order[inorder])
        if orderdict:
            orderlist.append(orderdict)
            print orderdict
            json['orderlist'] = orderlist
        else:
            json['orderlist'] = []
        #此处请查询assortment表 条件是i['room_people_id']
        jsontitle = {i['room_people_name']:json}
        data.append(jsontitle)
    print json_util.dumps(data,ensure_ascii=False,indent=2)
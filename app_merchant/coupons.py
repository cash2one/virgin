#--coding:utf-8--#
import json
from os import abort

import datetime

from app_merchant import auto
from tools import tools

from flask import Blueprint,request
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import  pymongo
mongo=conn.mongo_conn()
table = {'status': 'int',
         'type': 'int',
         'restaurant_id': 'obj',
         '_id': 'obj',
         'username':'str',
         'phone':'str',
         'demand':'str',
         'numpeople':'int',
         'preset_time':'',
         'kind':'str'
      }
coupons_api = Blueprint('coupons_api', __name__, template_folder='templates')
def checkcoupons(restaurant_id,):
    dict = {
        "button":"1",
        "restaurant_id" : ObjectId(restaurant_id),
        "type" : "1",
        "showtime_start" : datetime.datetime.now(),
        "showtime_end" : datetime.datetime.now(),
        "num" : -1,
        "cross-claim" : 0.0,
        "content" : "",
        "indate_start" : datetime.datetime.now(),
        "indate_end" : datetime.datetime.now(),
        "rule" : "0",
        "money" : 0.0,
        "kind" : "1",
    }
    dict2 = {
        "button":"1",
        "restaurant_id" : ObjectId(restaurant_id),
        "type" : "1",
        "showtime_start" : datetime.datetime.now(),
        "showtime_end" : datetime.datetime.now(),
        "num" : -1,
        "cross-claim" : 0.0,
        "content" : "",
        "indate_start" : datetime.datetime.now(),
        "indate_end" : datetime.datetime.now(),
        "rule" : "0",
        "money" : 0.0,
        "kind" : "2",
    }
    flag = True
    item = mongo.coupons.find({"restaurant_id":ObjectId(restaurant_id)})
    for i in item:
        flag = False
    # print json_util.dumps(item,ensure_ascii=False,indent=2) == []
    if flag:
        print 'in'
        mongo.coupons.insert(dict)
        mongo.coupons.insert(dict2)
#店粉优惠查询
@coupons_api.route('/fm/merchant/v1/coupons/findcoupons/', methods=['POST'])
def findcoupons():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                checkcoupons(request.form['restaurant_id'])
                pdict = {
                    'restaurant_id':request.form['restaurant_id'],
                    'kind':'1'
                    }
                kind = int(request.form['kind'])
                json={}
                if kind == 1:
                    item = mongo.coupons.find(tools.orderformate(pdict, table)).sort("addtime",pymongo.DESCENDING)
                    for i in item:
                        json = {}
                        for key in i.keys():
                            if key == '_id':
                                json['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                json['restaurant_id'] = str(i[key])
                            elif key == 'button':
                                json['button'] = i[key]
                            elif key == 'rule':
                                if i[key] == '0':
                                    json['rule'] = i[key]
                                    json['rulename'] = '无门槛'
                                elif i[key] == '1':
                                    json['rule'] = i[key]
                                    json['rulename'] = '全品满'+str(i['money'])+'元可使用'
                                elif i[key] == '2':
                                    json['rule'] = i[key]
                                    json['rulename'] = '菜品满'+str(i['money'])+'元可使用'
                                elif i[key] == '3':
                                    json['rule'] = i[key]
                                    json['rulename'] = '酒类满'+str(i['money'])+'元可使用'
                                else:
                                    json['rule'] = ''
                            elif key == 'showtime_start':
                                json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'content':
                                if i['type'] == '1':
                                    if i['rule'] == '0':
                                        json['content'] = '下单即减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '1':
                                        json['content'] = '全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '2':
                                        json['content'] = '菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '3':
                                        json['content'] = '酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    else:
                                        pass
                                elif i['type'] == '2':
                                    if i['rule'] == '0':
                                        json['content'] = '下单即打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '1':
                                        json['content'] = '全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '2':
                                        json['content'] = '菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '3':
                                        json['content'] = '酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    else:
                                        pass
                                else:
                                    json['content'] = i['content']
                            elif key == 'showtime_end':
                                json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                json['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                json['indate_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'addtime':
                                json['addtime'] = i[key].strftime('%Y年%m月%d日')
                            else:
                                json[key] = i[key]
                                json['status'] = ''
                elif kind == 2:
                    pdict['kind'] = 2
                    item = mongo.coupons.find(tools.orderformate(pdict, table)).sort("addtime",pymongo.DESCENDING)
                    for i in item:
                        json = {}
                        for key in i.keys():
                            if key == '_id':
                                json['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                json['restaurant_id'] = str(i[key])
                            elif key == 'button':
                                json['button'] = i[key]
                            elif key == 'rule':
                                if i[key] == '0':
                                    json['rule'] = i[key]
                                    json['rulename'] = '无门槛'
                                elif i[key] == '1':
                                    json['rule'] = i[key]
                                    json['rulename'] = '全品满'+str(i['money'])+'元可使用'
                                elif i[key] == '2':
                                    json['rule'] = i[key]
                                    json['rulename'] = '菜品满'+str(i['money'])+'元可使用'
                                elif i[key] == '3':
                                    json['rule'] = i[key]
                                    json['rulename'] = '酒类满'+str(i['money'])+'元可使用'
                                else:
                                    json['rule'] = ''
                            elif key == 'content':
                                if i['type'] == '1':
                                    if i['rule'] == '0':
                                        json['content'] = '下单即减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '1':
                                        json['content'] = '全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '2':
                                        json['content'] = '菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '3':
                                        json['content'] = '酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    else:
                                        pass
                                elif i['type'] == '2':
                                    if i['rule'] == '0':
                                        json['content'] = '下单即打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '1':
                                        json['content'] = '全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '2':
                                        json['content'] = '菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '3':
                                        json['content'] = '酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    else:
                                        pass
                                else:
                                    json['content'] = i['content']
                            elif key == 'showtime_start':
                                json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'showtime_end':
                                json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                json['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                json['indate_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'addtime':
                                json['addtime'] = i[key].strftime('%Y年%m月%d日')
                            else:
                                json[key] = i[key]
                                json['status'] = ''
                else:
                    pdict['kind'] = 3
                    pageindex = int(request.form['pageindex'])
                    pagenum = 10
                    star = (int(pageindex)-1)*pagenum
                    end = (pagenum*int(pageindex))
                    item = mongo.coupons.find(tools.orderformate(pdict, table)).sort("addtime",pymongo.DESCENDING)[star:end]

                    list = []
                    for i in item:
                        data = {}
                        for key in i.keys():
                            if key == '_id':
                                data['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                data['restaurant_id'] = str(i[key])
                            elif key == 'rule':
                                if i[key] == '0':
                                    data['rule'] = i[key]
                                    data['rulename'] = '无门槛'
                                elif i[key] == '1':
                                    data['rule'] = i[key]
                                    data['rulename'] = '全品满'+str(i['money'])+'元可使用'
                                elif i[key] == '2':
                                    data['rule'] = i[key]
                                    data['rulename'] = '菜品满'+str(i['money'])+'元可使用'
                                elif i[key] == '3':
                                    data['rule'] = i[key]
                                    data['rulename'] = '酒类满'+str(i['money'])+'元可使用'
                                else:
                                    data['rule'] = ''
                            elif key == 'content':
                                if i['type'] == '1':
                                    if i['rule'] == '0':
                                        data['content'] = '下单即减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '1':
                                        data['content'] = '全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '2':
                                        data['content'] = '菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    elif i['rule'] == '3':
                                        data['content'] = '酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                    else:
                                        pass
                                elif i['type'] == '2':
                                    if i['rule'] == '0':
                                        data['content'] = '下单即打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '1':
                                        data['content'] = '全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '2':
                                        data['content'] = '菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    elif i['rule'] == '3':
                                        data['content'] = '酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                    else:
                                        pass
                                else:
                                    data['content'] = i['content']
                            elif key == 'showtime_start':
                                data['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'showtime_end':
                                data['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                data['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                data['indate_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'addtime':
                                data['addtime'] = i[key].strftime('%Y年%m月%d日')
                            else:
                                data[key] = i[key]
                            if datetime.datetime.now()<i['indate_start']:
                                data['status'] = '未开始'
                            elif i['indate_start']<datetime.datetime.now()<i['indate_end']:
                                data['status'] = '进行中'
                            else:
                                data['status'] = '已结束'
                        list.append(data)
                    json['list'] = list
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                result=tool.return_json(0,"field",True,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",True,e)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
#店粉优惠 单条查询
@coupons_api.route('/fm/merchant/v1/coupons/couponsinfo/', methods=['POST'])
def couponsinfo():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                pdict = {
                    '_id':request.form['coupons_id']
                    }
                item = mongo.coupons.find(tools.orderformate(pdict, table))
                json = {}
                for i in item:
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                        elif key == 'kind':
                            if i[key] == '1' or i[key] == '2':
                                json['button'] = i[key]
                        elif key == 'rule':
                            if i[key] == '0':
                                json['rule'] = i[key]
                                json['rulename'] = '无门槛'
                            elif i[key] == '1':
                                json['rule'] = i[key]
                                json['rulename'] = '全品满'+str(i['money'])+'元可使用'
                            elif i[key] == '2':
                                json['rule'] = i[key]
                                json['rulename'] = '菜品满'+str(i['money'])+'元可使用'
                            elif i[key] == '3':
                                json['rule'] = i[key]
                                json['rulename'] = '酒类满'+str(i['money'])+'元可使用'
                            else:
                                json['rule'] = ''
                        elif key == 'content':
                            if i['type'] == '1':
                                if i['rule'] == '0':
                                    json['content'] = '下单即减'+str(i['cross-claim'])+'元'
                                elif i['rule'] == '1':
                                    json['content'] = '全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                elif i['rule'] == '2':
                                    json['content'] = '菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                elif i['rule'] == '3':
                                    json['content'] = '酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
                                else:
                                    pass
                            elif i['type'] == '2':
                                if i['rule'] == '0':
                                    json['content'] = '下单即打'+str(i['cross-claim'])+'折'
                                elif i['rule'] == '1':
                                    json['content'] = '全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                elif i['rule'] == '2':
                                    json['content'] = '菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                elif i['rule'] == '3':
                                    json['content'] = '酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
                                else:
                                    pass
                            else:
                                json['content'] = i['content']
                        elif key == 'showtime_start':
                            json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'showtime_end':
                            json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_start':
                            json['indate_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_end':
                            json['indate_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'addtime':
                            json['addtime'] = i[key].strftime('%Y年%m月%d日')
                        else:
                            json[key] = i[key]
                        if datetime.datetime.now()<i['indate_start']:
                                json['status'] = '未开始'
                        elif i['indate_start']<datetime.datetime.now()<i['indate_end']:
                            json['status'] = '进行中'
                        else:
                            json['status'] = '已结束'
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",True,e)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
#店粉优惠 添加
@coupons_api.route('/fm/merchant/v1/coupons/insertcoupons/', methods=['POST'])
def insertcoupons():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                pdict = {
                            "restaurant_id" : ObjectId(request.form['restaurant_id']),
                            "type" : request.form['type'],
                            "showtime_start" : datetime.datetime.strptime(request.form["showtime_start"], "%Y-%m-%d"),
                            "showtime_end" : datetime.datetime.strptime(request.form["showtime_end"], "%Y-%m-%d"),
                            "num" : int(request.form['num']),
                            "cross-claim" :0.0,
                            "content" : request.form['content'],
                            "indate_start" : datetime.datetime.strptime(request.form["indate_start"], "%Y-%m-%d"),
                            "indate_end" : datetime.datetime.strptime(request.form["indate_end"], "%Y-%m-%d"),
                            "rule" : request.form['rule'],
                            "money" : float(request.form['money']),
                            "kind" : "3",
                            "button":"0",
                            # "status" : 0
                            "addtime":datetime.datetime.now()   #hancuiyi
                        }
                if int(request.form['type']) == 1 or int(request.form['type']) == 2:
                    try:
                        if type(float(request.form['content'])) == float:
                            print '1'
                            pdict['cross-claim'] = float(request.form['content'])
                            item = mongo.coupons.insert(pdict)
                            json = {
                                "status": 1,
                                "msg":""
                            }
                            result=tool.return_json(0,"success",True,json)
                            return json_util.dumps(result,ensure_ascii=False,indent=2)
                        else:
                            result=tool.return_json(0,"金额或折扣必须为数字格式",True,None)
                            return json_util.dumps(result,ensure_ascii=False,indent=2)
                    except Exception,e:
                        print e
                        result=tool.return_json(0,"金额或折扣必须为数字格式",True,None)
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    item = mongo.coupons.insert(pdict)
                    json = {
                        "status": 1,
                        "msg":""
                    }
                    result=tool.return_json(0,"success",True,json)
                    return json_util.dumps(result,ensure_ascii=False,indent=2)

            else:
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",True,e)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
#店粉优惠 修改
@coupons_api.route('/fm/merchant/v1/coupons/updatecoupons/', methods=['POST'])
def updatecoupons():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                pdict = {
                            "restaurant_id" : ObjectId(request.form['restaurant_id']),
                            "type" : request.form['type'],
                            "showtime_start" : datetime.datetime.strptime(request.form["showtime_start"], "%Y-%m-%d"),
                            "showtime_end" : datetime.datetime.strptime(request.form["showtime_end"], "%Y-%m-%d"),
                            "num" : int(request.form['num']),
                            "content" : request.form['content'],
                            "indate_start" : datetime.datetime.strptime(request.form["indate_start"], "%Y-%m-%d"),
                            "indate_end" : datetime.datetime.strptime(request.form["indate_end"], "%Y-%m-%d"),
                            "rule" : request.form['rule'],
                            "money" : float(request.form['money']),
                            # "status" : request.form['status']
                            "addtime":datetime.datetime.now()   #hancuiyi
                        }
                if int(request.form['type']) == 1 or int(request.form['type']) == 2:
                    try:
                        if type(float(request.form['content'])) == float:
                            pdict['cross-claim'] = float(request.form['content'])
                            print '1'
                            item = mongo.coupons.update({"_id":ObjectId(request.form["coupons_id"])},{"$set":pdict})
                            json = {
                                "status": 1,
                                "msg":""
                            }
                            result=tool.return_json(0,"success",True,json)
                            return json_util.dumps(result,ensure_ascii=False,indent=2)
                        else:
                            result=tool.return_json(0,"金额或折扣必须为数字格式",True,None)
                            return json_util.dumps(result,ensure_ascii=False,indent=2)
                    except Exception,e:
                        print e
                        result=tool.return_json(0,"金额或折扣必须为数字格式",True,None)
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    item = mongo.coupons.update({"_id":ObjectId(request.form["coupons_id"])},{"$set":pdict})
                    json = {
                        "status": 1,
                        "msg":""
                    }
                    result=tool.return_json(0,"success",True,json)
                    return json_util.dumps(result,ensure_ascii=False,indent=2)

            else:
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",True,e)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
# #店粉优惠 删除
# @coupons_api.route('/fm/merchant/v1/coupons/deletecoupons/', methods=['POST'])
# def deletecoupons():
#     if request.method=='POST':
#         try:
#             if auto.decodejwt(request.form['jwtstr']):
#                 item = mongo.coupons.update({"_id":ObjectId(request.form["coupons_id"])},{"$set":{"status":1}})
#                 json = {
#                     "status": 1,
#                     "msg":""
#                 }
#                 result=tool.return_json(0,"success",True,json)
#                 return json_util.dumps(result,ensure_ascii=False,indent=2)
#             else:
#                 result=tool.return_json(0,"field",False,None)
#                 return json_util.dumps(result,ensure_ascii=False,indent=2)
#         except Exception,e:
#             print e
#             result=tool.return_json(0,"field",False,None)
#             return json_util.dumps(result,ensure_ascii=False,indent=2)
#
#     else:
#         return abort(403)
#店粉优惠 扫码查询
@coupons_api.route('/fm/merchant/v1/coupons/couponsbyqr/', methods=['POST'])
def couponsbyqr():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                user_id = request.form['webuser_id']
                json={}
                item = mongo.coupons.find({"restaurant_id":ObjectId(request.form["restaurant_id"]),"kind":"1"}).sort("addtime",pymongo.DESCENDING)
                kind1 = {}
                for i in item:
                    print i
                    for key in i.keys():
                        if key == '_id':
                            kind1['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            kind1['restaurant_id'] = str(i[key])
                        elif key == 'rule':
                            if i[key] == '0':
                                kind1['rule'] = i[key]
                                kind1['rulename'] = '无门槛'
                            elif i[key] == '1':
                                kind1['rule'] = i[key]
                                kind1['rulename'] = '全品满'
                            elif i[key] == '2':
                                kind1['rule'] = i[key]
                                kind1['rulename'] = '菜品满'
                            elif i[key] == '3':
                                kind1['rule'] = i[key]
                                kind1['rulename'] = '酒类满'
                            else:
                                kind1['rule'] = ''
                        elif key == 'showtime_start':
                            kind1['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'showtime_end':
                            kind1['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_start':
                            kind1['indate_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_end':
                            kind1['indate_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'addtime':
                            kind1['addtime'] = i[key].strftime('%Y年%m月%d日')
                        else:
                            kind1[key] = i[key]


                item = mongo.coupons.find({"restaurant_id":ObjectId(request.form["restaurant_id"]),"kind":"2"}).sort("addtime",pymongo.DESCENDING)
                kind2 = {}
                for i in item:

                    for key in i.keys():
                        if key == '_id':
                            kind2['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            kind2['restaurant_id'] = str(i[key])
                        elif key == 'rule':
                            if i[key] == '0':
                                kind2['rule'] = i[key]
                                kind2['rulename'] = '无门槛'
                            elif i[key] == '1':
                                kind2['rule'] = i[key]
                                kind2['rulename'] = '全品满'
                            elif i[key] == '2':
                                kind2['rule'] = i[key]
                                kind2['rulename'] = '菜品满'
                            elif i[key] == '3':
                                kind2['rule'] = i[key]
                                kind2['rulename'] = '酒类满'
                            else:
                                kind2['rule'] = ''
                        elif key == 'showtime_start':
                            kind2['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'showtime_end':
                            kind2['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_start':
                            kind2['indate_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_end':
                            kind2['indate_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'addtime':
                            kind2['addtime'] = i[key].strftime('%Y年%m月%d日')
                        else:
                            kind2[key] = i[key]

                item = mongo.coupons.find({"restaurant_id":ObjectId(request.form["restaurant_id"]),"kind":"3"}).sort("addtime",pymongo.DESCENDING)[0:1]
                kind3 = {}
                for i in item:

                    for key in i.keys():
                        if key == '_id':
                            kind3['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            kind3['restaurant_id'] = str(i[key])
                        elif key == 'rule':
                            if i[key] == '0':
                                kind3['rule'] = i[key]
                                kind3['rulename'] = '无门槛'
                            elif i[key] == '1':
                                kind3['rule'] = i[key]
                                kind3['rulename'] = '全品满'
                            elif i[key] == '2':
                                kind3['rule'] = i[key]
                                kind3['rulename'] = '菜品满'
                            elif i[key] == '3':
                                kind3['rule'] = i[key]
                                kind3['rulename'] = '酒类满'
                            else:
                                kind3['rule'] = ''
                        elif key == 'showtime_start':
                            kind3['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'showtime_end':
                            kind3['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_start':
                            kind3['indate_start'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'indate_end':
                            kind3['indate_end'] = i[key].strftime('%Y年%m月%d日')
                        elif key == 'addtime':
                            kind3['addtime'] = i[key].strftime('%Y年%m月%d日')
                        else:
                            kind3[key] = i[key]
                        if datetime.datetime.now()<i['indate_start']:
                            kind3['status'] = '未开始'
                        elif i['indate_start']<datetime.datetime.now()<i['indate_end']:
                            kind3['status'] = '进行中'
                        else:
                            kind3['status'] = '已结束'
                json['kind1'] = kind1
                json['kind2'] = kind2
                json['kind3'] = kind3
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception, e:
            print e
            result=tool.return_json(0,"field",True,e)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
#店粉优惠 修改button启用开关
@coupons_api.route('/fm/merchant/v1/coupons/updatebutton/', methods=['POST'])
def updatebutton():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                item = mongo.coupons.update({"_id":ObjectId(request.form["coupons_id"])},{"$set":{"button":str(request.form["button"])}})
                json = {
                    "status": 1,
                    "msg":""
                }
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)

    else:
        return abort(403)
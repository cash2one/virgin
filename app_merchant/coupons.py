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
#店粉优惠查询
@coupons_api.route('/fm/merchant/v1/coupons/findcoupons/', methods=['POST'])
def findcoupons():
    if request.method=='POST':
        try:
            if auto.decodejwt(request.form['jwtstr']):
                pdict = {
                    'restaurant_id':request.form['restaurant_id'],
                    'kind':'1',
                    # 'status':0
                    }
                kind = int(request.form['kind'])
                json={}
                if kind == 1:
                    item = mongo.coupons.find(tools.orderformate(pdict, table))
                    for i in item:
                        json = {}
                        for key in i.keys():
                            if key == '_id':
                                json['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                json['restaurant_id'] = str(i[key])
                            elif key == 'showtime_start':
                                json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'showtime_end':
                                json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                json['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                json['indate_end'] = i[key].strftime('%Y年%m月%d日')
                            else:
                                json[key] = i[key]
                elif kind == 2:
                    pdict['kind'] = 2
                    item = mongo.coupons.find(tools.orderformate(pdict, table))
                    for i in item:
                        json = {}
                        for key in i.keys():
                            if key == '_id':
                                json['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                json['restaurant_id'] = str(i[key])
                            elif key == 'showtime_start':
                                json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'showtime_end':
                                json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                json['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                json['indate_end'] = i[key].strftime('%Y年%m月%d日')
                            else:
                                json[key] = i[key]
                else:
                    pdict['kind'] = 3
                    pageindex = int(request.form['pageindex'])
                    pagenum = 10
                    star = (int(pageindex)-1)*pagenum
                    end = (pagenum*int(pageindex))
                    item = mongo.coupons.find(tools.orderformate(pdict, table))[star:end]

                    list = []
                    for i in item:
                        data = {}
                        for key in i.keys():
                            if key == '_id':
                                data['id'] = str(i[key])
                            elif key == 'restaurant_id':
                                data['restaurant_id'] = str(i[key])
                            elif key == 'showtime_start':
                                data['showtime_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'showtime_end':
                                data['showtime_end'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_start':
                                data['indate_start'] = i[key].strftime('%Y年%m月%d日')
                            elif key == 'indate_end':
                                data['indate_end'] = i[key].strftime('%Y年%m月%d日')
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
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
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
            result=tool.return_json(0,"field",False,None)
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
                            "kind" : "3"
                            # "status" : 0
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
            result=tool.return_json(0,"field",False,None)
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
            result=tool.return_json(0,"field",False,None)
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
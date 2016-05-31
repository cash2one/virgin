#--coding:utf-8--#
from os import abort

from app_merchant import auto
from tools import tools

from flask import Blueprint,request
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool

import connect

table = {'status': 'int',
         'type': 'int',
         'restaurant_id': 'obj',
         '_id': 'obj',
         'menu.dish_type':'str',
      }
dishes_discount = {
    'dishes_discount.discount':'int',
    'dishes_discount.message':'str',
    'dishes_discount.end_time':'str',
    'dishes_discount.start_time':'str',
    'dishes_discount.desc':'str',
}

mongo=conn.mongo_conn()

restaurant_api = Blueprint('restaurant_api', __name__, template_folder='templates')

#1.4菜品优惠查询form:id
@restaurant_api.route('/fm/merchant/v1/restaurant/restaurant_discount/', methods=['POST'])
def restaurant_discount():
    try:
        pdict = {
            '_id':request.form["id"],
            'menu.dish_type':request.form['dish_type']
        }
        item = mongo.restaurant.find(tools.orderformate(pdict, table),{})
        data={}
        list = []
        for i in item:
            json = {}
            for key in i.keys():
                if key == '_id':
                    json['id'] = i[key]
                else:
                    json[key] = i[key]
            list.append(json)
        data['list'] = list
        jwtmsg = auto.decodejwt(request.form["jwtstr"])
        result=tool.return_json(0,"success",jwtmsg,data)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
    except Exception,e:
        print e
        result=tool.return_json(0,"field",False,None)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
#修改菜品价格
# @restaurant_api.route('/fm/merchant/v1/restaurant/updaterestaurant/', methods=['POST'])
# def updaterestaurant():
#     try:
#         pdict = {
#             "dishes_discount.discount":request.form['discount'],
#             "dishes_discount.message":request.form['message'],
#             "dishes_discount.end_time":request.form['end_time'],
#             "dishes_discount.start_time":request.form['start_time'],
#             "dishes_discount.desc":request.form['desc']
#         }
#         objid = {"_id":ObjectId(request.form["id"])}
#         first = tools.orderformate(pdict,dishes_discount)
#         second = {"$set":first}
#         mongo.restaurant.update_one(objid,second)
#
#         dish = {
#             request.form['dish_id']: {'discount_price': float(request.form['discount_price'])}
#         }
#         redish = tool.Foormat(request.form["id"]).re_dish(dish)
#         redish.submit2db()
#         json = {
#                 "status": 1,
#                 "msg":""
#         }
#         jwtmsg = auto.decodejwt(request.form["jwtstr"])
#         result=tool.return_json(0,"success",jwtmsg,json)
#         return json_util.dumps(result,ensure_ascii=False,indent=2)
#     except Exception,e:
#         print e
#         result=tool.return_json(0,"field",False,None)
#         return json_util.dumps(result,ensure_ascii=False,indent=2)
#平台优惠 查询菜品优惠信息
@restaurant_api.route('/fm/merchant/v1/restaurant/dishes_discountinfos/', methods=['POST'])
def dishes_discountinfos():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"dishes_discount.discount":1,"dishes_discount.message":1,"dishes_discount.start_time":1,"dishes_discount.end_time":1,"_id":1})
            for i in item:
                json = {}
                for key in i.keys():
                    if key == '_id':
                        json['id'] = str(i[key])
                    elif key == 'dishes_discount':
                        json['discount'] = i["dishes_discount"]["discount"]
                        json['message'] = i["dishes_discount"]["message"]
                        json['start_time'] = i["dishes_discount"]["start_time"]
                        json['end_time'] = i["dishes_discount"]["end_time"]
                    else:
                        json[key] = i[key]

            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 查询酒水优惠信息
@restaurant_api.route('/fm/merchant/v1/restaurant/wine_discountinfos/', methods=['POST'])
def wine_discountinfos():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"wine_discount.message":1,"wine_discount.start_time":1,"wine_discount.end_time":1,"_id":1})
            for i in item:
                json = {}
                for key in i.keys():
                    if key == '_id':
                        json['id'] = str(i[key])
                    elif key == 'wine_discount':
                        json['message'] = i["wine_discount"]["message"]
                        json['start_time'] = i["wine_discount"]["start_time"]
                        json['end_time'] = i["wine_discount"]["end_time"]
                    else:
                        json[key] = i[key]

            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 查询其他优惠信息
@restaurant_api.route('/fm/merchant/v1/restaurant/restaurant_discountinfos/', methods=['POST'])
def restaurant_discountinfos():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"restaurant_discount.message":1,"restaurant_discount.start_time":1,"restaurant_discount.end_time":1,"_id":1})
            for i in item:
                json = {}
                for key in i.keys():
                    if key == '_id':
                        json['id'] = str(i[key])
                    elif key == 'restaurant_discount':
                        json['message'] = i["restaurant_discount"]["message"]
                        json['start_time'] = i["restaurant_discount"]["start_time"]
                        json['end_time'] = i["restaurant_discount"]["end_time"]
                    else:
                        json[key] = i[key]

            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 菜品优惠 修改菜品优惠包括全单折扣
@restaurant_api.route('/fm/merchant/v1/restaurant/updatediscount/', methods=['POST'])
def updatediscount():
    if request.method=='POST':
        try:
            pdict = {
                "dishes_discount.discount":float(request.form["discount"]),
                "dishes_discount.message":request.form["message"],
                "dishes_discount.start_time":request.form["start_time"],
                "dishes_discount.end_time":request.form["end_time"]
            }
            mongo.restaurant.update_one({"_id":ObjectId(request.form["restaurant_id"])},{"$set":pdict})
            json = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 菜品优惠 修改酒水优惠
@restaurant_api.route('/fm/merchant/v1/restaurant/updatewine_discount/', methods=['POST'])
def updatewine_discount():
    if request.method=='POST':
        try:
            pdict = {
                "wine_discount.message":request.form["message"],
                "wine_discount.start_time":request.form["start_time"],
                "wine_discount.end_time":request.form["end_time"]
            }
            mongo.restaurant.update_one({"_id":ObjectId(request.form["restaurant_id"])},{"$set":pdict})
            json = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 菜品优惠 修改其他优惠
@restaurant_api.route('/fm/merchant/v1/restaurant/updaterestaurant_discount/', methods=['POST'])
def updaterestaurant_discount():
    if request.method=='POST':
        try:
            pdict = {
                "restaurant_discount.message":request.form["message"],
                "restaurant_discount.start_time":request.form["start_time"],
                "restaurant_discount.end_time":request.form["end_time"]
            }
            mongo.restaurant.update_one({"_id":ObjectId(request.form["restaurant_id"])},{"$set":pdict})
            json = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 菜品优惠 查询所有菜品
@restaurant_api.route('/fm/merchant/v1/restaurant/dishsinfos/', methods=['POST'])
def dishsinfos():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"menu":1})
            dishs_dict ={}
            dishs_list =[]
            for i in item:

                for i in i['menu']:

                    if i['name'] !='酒水' and i['dish_type'] =='1' and i['dishs']!=[]:
                        for dish in i['dishs']:
                            json = {}
                            json['dish_id'] = dish['id']
                            json['price'] = dish['price']
                            json['name'] = dish['name']
                            json['discount_price'] = dish['discount_price']
                            dishs_list.append(json)
            dishs_dict['list'] = dishs_list
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,dishs_dict)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#平台优惠 菜品优惠 修改所有菜品特价
@restaurant_api.route('/fm/merchant/v1/restaurant/updatedishs/', methods=['POST'])
def updatedishs():
    import json
    if request.method=='POST':
        try:
            # json = {
            #     '201605111041429997': {'discount_price': 55555555555555555555.00},
            #     '201605111040002332': {'discount_price': 22222222222222222222222222222.00}
            # }
            redish = request.form['redish']
            print type(redish),redish
            jsonredish = json.loads(redish)
            print type(jsonredish),jsonredish
            first = tool.Discount(request.form["restaurant_id"])
            first.re_dish(jsonredish)
            first.submit2db()


            json = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
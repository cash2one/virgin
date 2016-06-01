#--coding:utf-8--#
import json
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

#菜品优惠 查询所有优惠信息 参数  restaurant_id
@restaurant_api.route('/fm/merchant/v1/restaurant/findalldis/', methods=['POST'])
def findalldis():
    if request.method=='POST':
        try:
            type = int(request.form['type'])
            alldata = {}
            dishs_list = []
            wine_list =[]
            item = mongo.restaurant.find({"_id":ObjectId(request.form["restaurant_id"])})

            for i in item:
                json = {}
                for key in i.keys():
                    #1菜品优惠信息开始
                    if key == 'dishes_discount':
                        json['discount'] = i["dishes_discount"]["discount"]
                        json['message'] = i["dishes_discount"]["message"]
                        json['start_time'] = i["dishes_discount"]["start_time"]
                        json['end_time'] = i["dishes_discount"]["end_time"]
                if type == 1:
                    alldata['dishes_discount'] = json
                    #1菜品优惠信息结束
                #2酒水优惠信息开始
                winejson = {}
                for winekey in i.keys():
                    if winekey == 'wine_discount':
                        winejson['discount'] = i["wine_discount"]["discount"]
                        winejson['message'] = i["wine_discount"]["message"]
                        winejson['start_time'] = i["wine_discount"]["start_time"]
                        winejson['end_time'] = i["wine_discount"]["end_time"]
                if type == 2:
                    alldata['wine_discount'] = winejson
                #2酒水优惠信息结束
                #3查询所有菜开始
                for dishs in i['menu']:
                    if dishs['name'] !='酒水' and dishs['name'] !='优惠菜' and dishs['name'] !='推荐菜' and dishs['dish_type'] =='1' and dishs['dishs']!=[]:
                        for dish in dishs['dishs']:
                            json = {}
                            json['dish_id'] = dish['id']
                            json['price'] = dish['price']
                            json['name'] = dish['name']
                            json['discount_price'] = dish['discount_price']
                            json['type'] = dish['type']
                            dishs_list.append(json)
                if type == 1:
                    alldata['dishs_list'] = dishs_list
                #查询所有菜结束
                #查询所有酒水开始
                for wines in i['menu']:
                    if wines['name'] =='酒水' and wines['dish_type'] =='1' and wines['dishs']!=[]:
                        for dish in wines['dishs']:
                            json = {}
                            json['dish_id'] = dish['id']
                            json['price'] = dish['price']
                            json['name'] = dish['name']
                            json['discount_price'] = dish['discount_price']
                            json['type'] = dish['type']
                            wine_list.append(json)
                if type == 1:
                    alldata['wine_list'] = wine_list
                #查询所有酒水结束
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,alldata)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#菜品优惠 修改所有
@restaurant_api.route('/fm/merchant/v1/restaurant/updatealldis/', methods=['POST'])
def updatealldis():
    if request.method=='POST':
        try:
            type = int(request.form['type'])
            if type == 1:
                pdict = {
                            "dishes_discount.discount":float(request.form["dishes_discount"]),
                            "dishes_discount.message":request.form["dishes_message"],
                            "dishes_discount.start_time":request.form["dishes_start_time"],
                            "dishes_discount.end_time":request.form["dishes_end_time"]

                        }
            elif type == 2:
                pdict = {
                            "wine_discount.discount":float(request.form["wine_discount"]),
                            "wine_discount.message":request.form["wine_message"],
                            "wine_discount.start_time":request.form["wine_start_time"],
                            "wine_discount.end_time":request.form["wine_end_time"]
                        }
            mongo.restaurant.update_one({"_id":ObjectId(request.form["restaurant_id"])},{"$set":pdict})
            # redish = {'201605111041429997':{'discount_price': 5555.00},'201605111040002332':{'discount_price':2222.00}}
            redish = request.form['redish']
            jsonredish = json.loads(redish)
            first = tool.Discount(request.form["restaurant_id"])
            first.re_dish(jsonredish)
            first.submit2db()
            jsons = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,jsons)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#菜单修改-查询菜单分类
@restaurant_api.route('/fm/merchant/v1/restaurant/menutypes/', methods=['POST'])
def menutypes():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"menu.name":1,"menu.id":1,"_id":0})
            data={}
            list = []
            for i in item:
                for j in i['menu']:
                    #如果需要修改优惠菜和推荐菜 就取消下面这句判断 暂定只修改菜品和酒水
                    if j['name'] !='优惠菜' and j['name'] !='推荐菜':
                        list.append(j)
            data['list'] = list
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,data)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#菜单修改-按照标签查询菜品和酒的集合
@restaurant_api.route('/fm/merchant/v1/restaurant/redishslist/', methods=['POST'])
def redishslist():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"menu":1})
            dishs_dict ={}
            dishs_list =[]
            for i in item:

                for dishs in i['menu']:
                    if dishs['name'] !='优惠菜' and dishs['name'] !='推荐菜' and dishs['dish_type'] =='1' and dishs['dishs']!=[]:
                        for dish in dishs['dishs']:
                            json = {}
                            json['dish_id'] = dish['id']
                            json['price'] = dish['price']
                            json['name'] = dish['name']
                            json['discount_price'] = dish['discount_price']
                            json['type'] = dish['type']
                            dishs_list.append(json)
            dishs_dict['dishs_list'] = dishs_list
            jwtmsg =auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,dishs_dict)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#mongo.restaurant.find({"_id":ObjectId("57329e300c1d9b2f4c85f8e6")},{"menu.name":1,"menu.id":1,"_id":0})
#菜单修改-查询单独菜单的菜和酒水 参数是菜单分类 dish_id
@restaurant_api.route('/fm/merchant/v1/restaurant/redishsinfos/', methods=['POST'])
def redishsinfos():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form["restaurant_id"]
            }
            item = mongo.restaurant.find(tools.orderformate(pdict, table),{"menu":1})
            dishs_dict ={}
            dishs_list =[]
            for i in item:

                for j in i['menu']:

                    if j['name'] !='优惠菜' and j['name'] !='推荐菜' and j['dish_type'] =='1' and j['dishs']!=[]:
                        for dish in j['dishs']:
                            json = {}
                            # if j['id'] == '201605111038236622':
                            if j['id'] == request.form["dish_id"]:
                                json['dish_id'] = dish['id']
                                json['price'] = dish['price']
                                json['name'] = dish['name']
                                json['discount_price'] = dish['discount_price']
                                json['type'] = dish['type']
                                json['guide_image'] = dish['guide_image']
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
#菜单修改-修改菜品和酒水
@restaurant_api.route('/fm/merchant/v1/restaurant/updatedishs/', methods=['POST'])
def updatedishs():
    if request.method=='POST':
        try:
            redish = {str(request.form['dish_id']):{'price': float(request.form['price']), 'name':request.form['name'],'guide_image':request.form['guide_image'],'type':request.form['type']}}
            # redish = request.form['redish']
            # jsonredish = json.loads(redish)
            first = tool.Discount(request.form["restaurant_id"])
            first.re_dish(redish)
            first.submit2db()
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            jsons = {
                    "status": 1,
                    "msg":""
            }
            result=tool.return_json(0,"success",jwtmsg,jsons)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#菜单修改-添加菜品和酒水
@restaurant_api.route('/fm/merchant/v1/restaurant/insertdishs/', methods=['POST'])
def insertdishs():
    if request.method=='POST':
        try:
            redish = {str(tool.gen_rnd_filename()):{'price': float(request.form['price']), 'name':request.form['name'], 'guide_image':request.form['guide_image'], 'type':request.form['type']}}
            # redish = request.form['redish']
            # jsonredish = json.loads(redish)
            first = tool.Discount(request.form["restaurant_id"])
            first.re_dish(redish)
            first.submit2db()
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            jsons = {
                    "status": 1,
                    "msg":""
            }
            result=tool.return_json(0,"success",jwtmsg,jsons)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)

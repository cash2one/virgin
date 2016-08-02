#--coding:utf-8--#
import random

import pymongo
from flasgger import swag_from

from app_merchant import auto
from tools import tools

import sys

from tools.db_app_user import guess, business_dist, district_list, business_dist_byid, getcoupons, getconcern
from tools.swagger import swagger

reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime

mongo=conn.mongo_conn()

restaurant_user_api = Blueprint('restaurant_user_api', __name__, template_folder='templates')





restaurant = swagger("饭店","饭店条件查询")
restaurant_json = {
    "auto": restaurant.String(description='验证是否成功'),
    "message": restaurant.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": restaurant.Integer(description='',default=0),
    "data": {
        "list": [
              {
                "distance": restaurant.String(description='距离，单位是米',default="1983"),
                "wine_discount": restaurant.String(description='酒水优惠',default=""),
                "kind3": restaurant.String(description='店粉抢优惠',default=""),
                "name": restaurant.String(description='饭店名',default="星晨烧烤"),
                "kind1": restaurant.String(description='店粉关注即享',default=""),
                "address": restaurant.String(description='地址',default="哈尔滨市南岗区平公街7-5号"),
                "id": restaurant.String(description='饭店id',default="573542780c1d9b34722f5da9"),
                "guide_image": restaurant.String(description='图片',default="09bb491fcde04edd99e898720c3918df"),
                "district_name": restaurant.String(description='区名',default="南岗区"),
                "business_name": restaurant.String(description='商圈名',default="十字/平公"),
                "restaurant_discount": restaurant.String(description='其他优惠',default=""),
                "dishes_discount": restaurant.String(description='菜品优惠',default=""),
                "kind2": restaurant.String(description='新粉优惠',default=""),
                "concern":restaurant.String(description='关注状态0未关注1已关注',default="0")
              }
        ]
    }
}
restaurant.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant.add_parameter(name='dishes_type',parametertype='formData',type='string',required= True,description='菜系，格式id_id_id',default='10')
restaurant.add_parameter(name='discount',parametertype='formData',type='string',required= True,description='优惠',default='dish')
restaurant.add_parameter(name='room_people_id',parametertype='formData',type='string',required= True,description='包房id',default='40')
restaurant.add_parameter(name='room_type',parametertype='formData',type='string',required= True,description='包房特色，格式id_id_id',default='36')
restaurant.add_parameter(name='tese',parametertype='formData',type='string',required= True,description='特色，格式id_id_id',default='51')
restaurant.add_parameter(name='pay_type',parametertype='formData',type='string',required= True,description='支付，格式id_id_id',default='48')
restaurant.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')
restaurant.add_parameter(name='x',parametertype='formData',type='string',required= True,description='坐标x，没有传x',default='126.62687122442075')
restaurant.add_parameter(name='y',parametertype='formData',type='string',required= True,description='坐标y，没有传y',default='45.764067772341264')
restaurant.add_parameter(name='business_dist_id',parametertype='formData',type='string',required= True,description='商圈id',default='45.764067772341264')
restaurant.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396fde7c1f31a9cce960fa')
#饭店列表 条件很多
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant/',methods=['POST'])
@swag_from(restaurant.mylpath(schemaid='restaurant',result=restaurant_json))
def restaurant():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                data = {}
# first = {"dishes_type.id":"10","dishes_discount.message":{"$ne":""},"rooms.room_type.id":"36","tese.id":"54","pay_type.id":{"$in":["48"]},"_id":{"$in":[ObjectId("57329e300c1d9b2f4c85f8e6")]}}
                first = {}
                #商圈
                if request.form['business_dist_id']!='-1':
                    first["business_dist.id"] = request.form['business_dist_id']
                #菜系
                if request.form['dishes_type']!='-1':
                    first["dishes_type.id"] = request.form['dishes_type']
                #饭店优惠
                if request.form['discount']!='-1':
                    if request.form['discount'] == 'dish':
                        first["dishes_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'wine':
                        first["wine_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'other':
                        first["restaurant_discount.message"] = {"$ne":""}
                    else:
                        pass
                #包房
                if request.form['room_people_id']!='-1':
                    first["rooms.room_people_id"] = request.form['room_people_id']
                #包房特色
                if request.form['room_type']!='-1':
                    b_idlist = request.form['room_type'].split('_')
                    bidlist = []
                    for mid in b_idlist:
                        if mid != '' and mid != None:
                            bidlist.append(mid)
                    first["rooms.room_type.id"] = {"$in":bidlist}
                #特色
                if request.form['tese']!='-1':
                    t_idlist = request.form['tese'].split('_')
                    tidlist = []
                    for mid in t_idlist:
                        if mid != '' and mid != None:
                            tidlist.append(mid)
                    first["tese.id"] = {"$in":tidlist}
                #支付
                if request.form['pay_type']!='-1':
                    pass
                    idlist = request.form['pay_type'].split('_')
                    midlist = []
                    for mid in idlist:
                        if mid != '' and mid != None:
                            midlist.append(mid)
                    first["pay_type.id"] = {"$in":midlist}
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                list = guess(first=first,lat1=float(request.form['y']),lon1=float(request.form['x']),start=star,end=end,webuser_id=request.form['webuser_id'])
                data['list'] = list
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)

#图片展示列表
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_img/',methods=['POST'])
def restaurant_img():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({'_id':ObjectId(request.form["restaurant_id"])})
                type = request.form['type']
                data ={}
                dishs_list =[]
                photo_list = []
                room_list = []
                for i in item:
                    #菜品图片 开始
                    if type == '1' or type == '-1':
                        for dishs in i['menu']:
                            if dishs['name'] !='优惠菜' and dishs['name'] !='推荐菜' and dishs['dish_type'] =='1' and dishs['dishs']!=[]:
                                for dish in dishs['dishs']:
                                    json = {}
                                    json['name'] = dish['name']
                                    json['guide_image'] = dish['guide_image']
                                    dishs_list.append(json)
                    #菜品图片 结束
                    #环境图片 开始
                    if type == '2' or type == '-1':
                        for photo in i['show_photos']:
                            pjson = {}
                            pjson['img'] = photo['img']
                            pjson['desc'] = photo['desc']
                            photo_list.append(pjson)
                    #环境图片 结束
                    #包房图片 开始
                    if type == '3' or type == '-1':
                        for room in i['rooms']:
                            for room_photo in room['room_photo']:
                                rjson = {}
                                rjson['img'] = room_photo['img']
                                rjson['desc'] = room_photo['desc']
                                room_list.append(rjson)
                    #包房图片 结束
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                dishs_list[0:0] = room_list
                dishs_list[0:0] = photo_list
                data['list'] = dishs_list[star:end]
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#饭店查询类别标签
restaurant_type = swagger("饭店","查询类别标签")
restaurant_type.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant_type_json = {
  "auto": restaurant_type.String(description='验证是否成功'),
  "code": restaurant_type.Integer(description='',default=0),
  "message": restaurant_type.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "data": {
    "baofang": [
      {
        "id": restaurant_type.String(description='包房id',default="39"),
        "name": restaurant_type.String(description='包房名',default="2-4人包房")
      }
    ],
    "baofangtese": [
      {
        "id": restaurant_type.String(description='包房特色id',default="36"),
        "name": restaurant_type.String(description='包房特色',default="带洗手间包房")
      }
    ],
    "fenlei": [
      {
        "id": restaurant_type.String(description='菜系id',default="2"),
        "name": restaurant_type.String(description='菜系名',default="快餐/小吃")
      }
    ],
    "zhifu": [
      {
        "id": restaurant_type.String(description='支付方式id',default="47"),
        "name": restaurant_type.String(description='支付方式',default="刷卡支付")
      }
    ],
    "tese": [
      {
        "id": restaurant_type.String(description='特色id',default="51"),
        "name": restaurant_type.String(description='特色',default="演艺")
      }
    ],
    "youhui": [
      {
        "id": restaurant_type.String(description='优惠类别',default="dish"),
        "name": restaurant_type.String(description='优惠类别名',default="菜品优惠")
      }
    ]
  },
}
#饭店查询类别标签
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_type/',methods=['POST'])
@swag_from(restaurant_type.mylpath(schemaid='restaurant_type',result=restaurant_type_json))
def restaurant_type():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                f_list = []
                b_list = []
                t_list = []
                z_list = []
                bt_list = []
                item = mongo.assortment.find({"parent":{"$in":[1,35,59,50,46]}})
                for i in item:
                    f_json = {}
                    b_json = {}
                    t_json = {}
                    z_json = {}
                    bt_json = {}
                    if i['parent'] == 1:
                        f_json['id'] = str(i['_id'])
                        f_json['name'] = i['name']
                        f_list.append(f_json)
                    elif i['parent'] == 35:
                        b_json['id'] = str(i['_id'])
                        b_json['name'] = i['name']
                        b_list.append(b_json)
                    elif i['parent'] == 59:
                        bt_json['id'] = str(i['_id'])
                        bt_json['name'] = i['name']
                        bt_list.append(bt_json)
                    elif i['parent'] == 50:
                        t_json['id'] = str(i['_id'])
                        t_json['name'] = i['name']
                        t_list.append(t_json)
                    elif i['parent'] == 46:
                        z_json['id'] = str(i['_id'])
                        z_json['name'] = i['name']
                        z_list.append(z_json)
                    else:
                        pass
                data['fenlei'] = f_list
                data['baofang'] = b_list
                data['baofangtese'] = bt_list
                data['tese'] = t_list
                data['zhifu'] = z_list
                data['youhui'] = [{'id':'dish','name':'菜品优惠'},{'id':'wine','name':'酒水优惠'},{'id':'other','name':'其他优惠'}]
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#根据坐标查询商圈
getbusiness_dist = swagger("饭店","根据坐标查询商圈")
getbusiness_dist.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
getbusiness_dist.add_parameter(name='longitude',parametertype='formData',type='string',required= True,description='经度',default='126.593666')
getbusiness_dist.add_parameter(name='latitude',parametertype='formData',type='string',required= True,description='纬度',default='45.706477')
getbusiness_dist_json = {
  "auto": getbusiness_dist.String(description='验证是否成功'),
  "message": getbusiness_dist.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": getbusiness_dist.Integer(description='',default=0),
  "data": {
    "biz_area_id": getbusiness_dist.String(description='商圈id',default='4193433'),
    "biz_area_name": getbusiness_dist.String(description='商圈名',default='哈西')
  }
}
#根据坐标查询商圈
@restaurant_user_api.route('/fm/user/v1/restaurant/getbusiness_dist/',methods=['POST'])
@swag_from(getbusiness_dist.mylpath(schemaid='getbusiness_dist',result=getbusiness_dist_json))
def getbusiness_dist():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                distance,id,name=business_dist(float(request.form['longitude']),float(request.form['latitude']))
                data = {
                    'biz_area_id':str(id),
                    'biz_area_name':str(name)
                }

                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#查询所有行政区
getdistrict_list = swagger("饭店","查询所有行政区")
getdistrict_list.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
getdistrict_list_json = {
  "auto": getdistrict_list.String(description='验证是否成功'),
  "message": getdistrict_list.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": getdistrict_list.Integer(description='',default=0),
  "data": {
        "district":[
            {
              "district_name": getdistrict_list.String(description='行政区名',default='南岗区'),
              "id": getdistrict_list.String(description='行政区id',default='56d7af296bff8928c07855dc')
            },
            {
              "district_name": getdistrict_list.String(description='行政区名',default='道里区'),
              "id": getdistrict_list.String(description='行政区id',default='5643898b4be1e3bc3c3cd7ff')
            },
            {
              "district_name": getdistrict_list.String(description='行政区名',default='香坊区'),
              "id": getdistrict_list.String(description='行政区id',default='5643898b4be1e3bc3c3cd801')
            },
        ]
    }
}
#查询所有行政区
@restaurant_user_api.route('/fm/user/v1/restaurant/getdistrict_list/',methods=['POST'])
@swag_from(getdistrict_list.mylpath(schemaid='getdistrict_list',result=getdistrict_list_json))
def getdistrict_list():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                list=district_list()
                data['district'] = list
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#根据行政区标签查询商圈
getbusiness_dist_byid = swagger("饭店","根据行政区标签查询商圈")
getbusiness_dist_byid.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
getbusiness_dist_byid.add_parameter(name='id',parametertype='formData',type='string',required= True,description='行政区id',default='56d95c1f0f884d3070fbdc4f')
getbusiness_dist_byid_json = {
  "auto": getbusiness_dist_byid.String(description='验证是否成功'),
  "message": getbusiness_dist_byid.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": getbusiness_dist_byid.Integer(description='',default=0),
  "data": {
    "biz_areas": [
      {
        "biz_area_name": getbusiness_dist_byid.String(description='商圈名',default="腾飞广场"),
        "biz_area_id": getbusiness_dist_byid.String(description='商圈id',default="13007"),
        "sort": getbusiness_dist_byid.String(description='排序',default="7"),
        "longitude": getbusiness_dist_byid.String(description='经度',default="122.535396"),
        "latitude": getbusiness_dist_byid.String(description='纬度',default="52.977977")
      },
      {
        "biz_area_name": getbusiness_dist_byid.String(description='商圈名',default="漠河火车站"),
        "biz_area_id": getbusiness_dist_byid.String(description='商圈id',default="13008"),
        "sort": getbusiness_dist_byid.String(description='排序',default="8"),
        "longitude": getbusiness_dist_byid.String(description='经度',default="122.518061"),
        "latitude": getbusiness_dist_byid.String(description='纬度',default="52.996306")
      }
    ]
  }
}
#根据行政区标签查询商圈
@restaurant_user_api.route('/fm/user/v1/restaurant/getbusiness_dist_byid/',methods=['POST'])
@swag_from(getbusiness_dist_byid.mylpath(schemaid='getbusiness_dist_byid',result=getbusiness_dist_byid_json))
def getbusiness_dist_byid():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data=business_dist_byid(request.form['id'])
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#关注饭店
concern = swagger("饭店","根据行政区标签查询商圈")
concern.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
concern.add_parameter(name='id',parametertype='formData',type='string',required= True,description='行政区id',default='56d95c1f0f884d3070fbdc4f')
concern_json = {
  "auto": concern.String(description='验证是否成功'),
  "message": concern.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": concern.Integer(description='',default=0),
  "data": {

  }
}
#关注饭店
@restaurant_user_api.route('/fm/user/v1/restaurant/concern/',methods=['POST'])
@swag_from(concern.mylpath(schemaid='concern',result=concern_json))
def concern():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {
                    "restaurant_id" : ObjectId(request.form['restaurant_id']),
                    "webuser_id" : ObjectId(request.form['webuser_id']),
                    "addtime" : datetime.datetime.now()
                }
                mongo.concern.insert(data)
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#关注饭店
restaurant_info = swagger("饭店","根据行政区标签查询商圈")
restaurant_info.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant_info.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='5798021b7c1fa230d18fdc70')
restaurant_info.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
restaurant_info_json = {
  "auto": restaurant_info.String(description='验证是否成功'),
  "message": restaurant_info.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": restaurant_info.Integer(description='',default=0),
  "data": {
          "wine_discount": restaurant_info.String(description='酒水优惠',default="1900臻藏6元、勇闯天涯3元"),
          "WiFi": restaurant_info.String(description='WiFi',default="有"),
          "rooms": {
            "room_name": restaurant_info.String(description='WiFi',default="中包（1间） 大包（1间）"),
            "room_type": restaurant_info.String(description='包房特色',default="")
          },
          "name": restaurant_info.String(description='饭店名',default="阿东海鲜老菜馆"),
          "shuaka": restaurant_info.String(description='是否能刷卡1是0否',default="0"),
          "weixin": restaurant_info.String(description='是否能微信支付1是0否',default="1"),
          "yanyi": restaurant_info.String(description='特色：演绎',default="无"),
          "dishes_type": restaurant_info.String(description='菜品类别',default="川菜/湘菜  炒菜"),
          "zhifubao": restaurant_info.String(description='是否能支付宝支付1是0否',default="0"),
          "24xiaoshi": restaurant_info.String(description='特色：24小时营业',default="无"),
          "dishes_discount": restaurant_info.String(description='菜品优惠',default="菜品8.5折,猪手10元/只、蚬子9.8元"),
          "phone": restaurant_info.String(description='饭店电话',default="15045681388"),
          "show_photos": [
            {
              "img": restaurant_info.String(description='饭店图片',default="6a84a308201d546aeb5dfd850ec7ae40"),
              "desc": restaurant_info.String(description='饭店图片排序，默认无序',default="")
            },
            {
              "img": restaurant_info.String(description='饭店图片',default="6ad56fdd7b8d97903dd036d8ffd8ea60"),
              "desc": restaurant_info.String(description='饭店图片排序，默认无序',default="")
            }
          ],
          "tingchechang": restaurant_info.String(description='特色：停车场',default="无"),
          "address": restaurant_info.String(description='饭店地址',default="哈尔滨市南岗区马家街132-2号"),
          "photos_num": restaurant_info.Integer(description='饭店图片数量',default=2),
          "tuijiancai": [
            {
              "name": restaurant_info.String(description='推荐菜名',default="小仁鲜"),
              "id": restaurant_info.String(description='推荐菜id',default="201605111053268902")
            }
          ],
          "open": restaurant_info.String(description='营业时间',default="9:00-23:00"),
          "id": restaurant_info.String(description='饭店id',default="57329e300c1d9b2f4c85f8e6"),
          "coupons": {
            "content": restaurant_info.String(description='店粉抢优惠',default="下单即减3.0元"),
            "id": restaurant_info.String(description='店粉抢优惠id',default="578309097c1fa4826dce8fbb"),
          },
          "concern": restaurant_info.String(description='是否关注1是0否',default="1")
    }
}
#饭店详情
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_info/',methods=['POST'])
@swag_from(restaurant_info.mylpath(schemaid='restaurant_info',result=restaurant_info_json))
def restaurant_info():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                webuser_id = request.form['webuser_id']
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                data = {}
                for i in item:
                    data['id'] = str(i['_id'])
                    data['show_photos'] = i['show_photos']
                    data['photos_num'] = len(i['show_photos'])
                    data['name'] = i['name']
                    #是否支持点菜订座文字(暂时空着)
                    dishes_type = []
                    for type in i['dishes_type']:
                        dishes_type.append(type['name'])
                    data['dishes_type'] = '  '.join(dishes_type)
                    dishes_discount = ''
                    if i['dishes_discount']['discount'] != 1.0:
                        dishes_discount = '菜品'+str(i['dishes_discount']['discount']*10)+'折,'
                    dishes_discount += i['dishes_discount']['message']
                    data['dishes_discount'] =dishes_discount
                    wine_discount = ''
                    if i['wine_discount']['discount'] != 1.0:
                        wine_discount = '菜品'+str(i['wine_discount']['discount']*10)+'折,'
                    wine_discount += i['wine_discount']['message']
                    data['wine_discount'] =wine_discount
                    data['coupons'] =getcoupons('3',str(i['_id']))
                    #开团请客（暂时空着）
                    data['concern'] = getconcern(str(i['_id']),webuser_id)
                    data['address'] = i['address']
                    data['phone'] = i['phone']
                    data['open'] = i['open']
                    for tese in i['tese']:
                        data['yanyi'] = '有' if '51' == tese['id'] else '无'
                        data['24xiaoshi'] = '有' if '52' == tese['id'] else '无'
                        data['tingchechang'] = '有' if '53' == tese['id'] else '无'
                        data['WiFi'] = '有' if '54' == tese['id'] else '无'
                    for pay_type in i['pay_type']:
                        data['shuaka'] = '1' if '47' == pay_type['id'] else '0'
                        data['weixin'] = '1' if '48' == pay_type['id'] else '0'
                        data['zhifubao'] = '1' if '49' == pay_type['id'] else '0'
                    room_name = []
                    rooms = {}
                    for room in i['rooms']:
                        if room['room_name'] != '大厅':
                            room_name.append(room['room_name'])
                        if room['room_type'] !=[]:
                            rooms['room_type'] = room['room_type'][0]['name']
                    rooms['room_name'] = ' '.join(room_name)
                    data['rooms'] = rooms
                    for menu in  i['menu']:
                        if menu['name'] == '推荐菜':
                            data['tuijiancai'] = menu['dishs']
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
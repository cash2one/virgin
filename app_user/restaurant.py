#--coding:utf-8--#
import random

import pymongo
from flasgger import swag_from

from app_merchant import auto
from tools import tools

import sys

from tools.db_app_user import guess, business_dist, district_list, business_dist_byid, getcoupons, getconcern
from tools.message_template import mgs_template
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





restaurant = swagger("1 美食地图.jpg","饭店条件查询")
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
                "concern":restaurant.String(description='关注状态0未关注1已关注',default="0"),
                "liansuo":restaurant.String(description='0不是连锁店1是连锁店',default="0")
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
restaurant.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id,未登录传-1',default='57396ec17c1f31a9cce960f4')
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
                list = guess(first=first,lat1=request.form['y'],lon1=request.form['x'],start=star,end=end,webuser_id=request.form['webuser_id'])
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
restaurant_img = swagger("1-2-2 饭店图片.jpg","图片展示列表")
restaurant_img.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant_img.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店ID',default='57329e300c1d9b2f4c85f8e6')
restaurant_img.add_parameter(name='type',parametertype='formData',type='string',required= True,description='-1全部1菜品图2环境图3包房图',default='-1')
restaurant_img.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')
restaurant_img_json = {
    "auto": restaurant_img.String(description='验证是否成功'),
    "message": restaurant_img.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": restaurant_img.Integer(description='',default=0),
    "data": {
             "list": [
                  {
                    "img": restaurant_img.String(description='图片MD5',default="6a84a308201d546aeb5dfd850ec7ae40"),
                    "desc": restaurant_img.String(description='排序，基本没有',default="")
                  },
                  {
                    "img": restaurant_img.String(description='图片MD5',default="6ad56fdd7b8d97903dd036d8ffd8ea60"),
                    "desc": restaurant_img.String(description='排序，基本没有',default="")
                  }
             ]
        }
}
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_img/',methods=['POST'])
@swag_from(restaurant_img.mylpath(schemaid='restaurant_img',result=restaurant_img_json))
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
                            if  dishs['dish_type'] =='0' and dishs['dishs']!=[]:
                                for dish in dishs['dishs']:
                                    json = {}
                                    json['img'] = dish
                                    json['desc'] = ''
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
restaurant_type = swagger("1 美食地图.jpg","查询类别标签")
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
getbusiness_dist = swagger("1-1-0 位置.jpg","根据坐标查询商圈")
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
getdistrict_list = swagger("1-1-0 位置.jpg","查询所有行政区")
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
getbusiness_dist_byid = swagger("1-1-0 位置.jpg","根据行政区标签查询商圈")
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
concern = swagger("1 美食地图.jpg","关注饭店")
concern.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
concern.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
concern.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
concern_json = {
  "auto": concern.String(description='验证是否成功'),
  "message": concern.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": concern.Integer(description='',default=0),
  "data": {
        "status": concern.Integer(description='1成功',default=1),
        "concern":concern.String(description='关注状态0未关注1已关注',default="0"),
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
                item = mongo.concern.find({"restaurant_id" : ObjectId(request.form['restaurant_id']),"webuser_id" : ObjectId(request.form['webuser_id'])})
                flag = True
                for i in item:
                    flag = False
                if flag:
                    mongo.concern.insert(data)
                    json = {
                            "status": 1,
                            "concern":"1"
                    }
                else:
                    mongo.concern.remove({"restaurant_id" : ObjectId(request.form['restaurant_id']),"webuser_id" : ObjectId(request.form['webuser_id'])})
                    json = {
                            "status": 1,
                            "concern":"0"
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
#饭店详情
restaurant_info = swagger("1-2 饭店详情.jpg","饭店详情")
restaurant_info.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant_info.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
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
          "zc1":restaurant_info.Boolean(description='是否支持订座true false',default=True),
          "zc2":restaurant_info.Boolean(description='是否支持点菜true false',default=True),
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
                    data['zc1'] = i['zc1']
                    data['zc2'] = i['zc2']
                    if i['show_photos'] != []:
                        data['show_photos'] = i['show_photos'][0]
                        data['photos_num'] = len(i['show_photos'])
                    else:
                        data['show_photos'] = {"img": "","desc": ""}
                        data['photos_num'] = 0
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
                        else:
                            rooms['room_type'] = ''
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
#图片菜单
pic_menu = swagger("1-2-3 菜单-1.jpg","图片菜单")
pic_menu.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
pic_menu.add_parameter(name='type',parametertype='formData',type='string',required= True,description='标签分类1全部2推荐菜3酒水',default='1')
pic_menu.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
pic_menu_json = {
  "auto": pic_menu.String(description='验证是否成功'),
  "message": pic_menu.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": pic_menu.Integer(description='',default=0),
  "data": {
  "alldish": pic_menu.String(description='饭店id',default="['015a0f05de8146a45c0681ba64bc49f6','f71d4db90411bd4c598821a72aa217bb']"),
  "wine": [
    {
      "price": pic_menu.Float(description='原价',default=3.0),
      "discount_price": pic_menu.Float(description='优惠价',default=2.8),
      "name": pic_menu.String(description='酒水名',default="大雪花"),
      "id": pic_menu.String(description='酒水id',default="201605111054065811")
    }
  ],
  "id": pic_menu.String(description='饭店id',default="57329e300c1d9b2f4c85f8e6"),
  "tuijiancai": [
    {
      "price": pic_menu.Float(description='原价',default=29.8),
      "discount_price": pic_menu.Float(description='优惠价',default=28.8),
      "name": pic_menu.String(description='菜品名',default="小仁鲜"),
      "id": pic_menu.String(description='菜品id',default="201605111053268902")
    }
  ]
}
}
#图片菜单
@restaurant_user_api.route('/fm/user/v1/restaurant/pic_menu/',methods=['POST'])
@swag_from(pic_menu.mylpath(schemaid='pic_menu',result=pic_menu_json))
def pic_menu():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                type = request.form['type']
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                data = {}
                for i in item:
                    data['id'] = str(i['_id'])
                    tuijiancaislist = []
                    winelist = []
                    piclist = []
                    for menu in  i['menu']:
                        if menu['name'] == '推荐菜':
                            if menu['dishs'] !=[]:
                                for dish in menu['dishs']:
                                    dishs = {}
                                    dishs['name'] = dish['name']
                                    dishs['id'] = dish['id']
                                    dishs['price'] = dish['price']
                                    dishs['discount_price'] = dish['discount_price']
                                    tuijiancaislist.append(dishs)
                            else:
                                pass
                        elif menu['name'] == '酒水':
                            if menu['dishs'] !=[]:
                                for dish in menu['dishs']:
                                    dishs = {}
                                    dishs['name'] = dish['name']
                                    dishs['id'] = dish['id']
                                    dishs['price'] = dish['price']
                                    dishs['discount_price'] = dish['discount_price']
                                    winelist.append(dishs)
                            else:
                                pass
                        elif menu['dish_type'] == '0':
                            if menu['dishs'] !=[]:
                                piclist = menu['dishs']
                    if type == '1':
                        data['alldish'] = piclist
                    elif type == '2':
                        data['tuijiancai'] = tuijiancaislist
                    else:
                        data['wine'] = winelist
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
#点菜菜单
dish_menu = swagger("1-2-3 菜单-2.jpg","点菜菜单")
dish_menu.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
dish_menu.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
dish_menu.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
dish_menu_json = {
  "auto": dish_menu.String(description='验证是否成功'),
  "message": dish_menu.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": dish_menu.Integer(description='',default=0),
  "data": {
      "menu": [
        {
          "list": [
            {
              "is_discount": dish_menu.Boolean(description='惠标签，是否有优惠',default=True),
              "is_recommend": dish_menu.Boolean(description='推荐标签，是否推荐',default=True),
              "id": dish_menu.String(description='菜品id',default="201605111053268902"),
              "price": dish_menu.Float(description='菜品原价',default=29.8),
              "num": dish_menu.Integer(description='点菜数量',default=0),
              "guide_image":dish_menu.String(description='图片，基本没有，留着以后用',default="MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5"),
              "name": dish_menu.String(description='菜品名',default="小仁鲜"),
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8)
            },
            {
              "is_discount": dish_menu.Boolean(description='惠标签，是否有优惠',default=True),
              "is_recommend": dish_menu.Boolean(description='推荐标签，是否推荐',default=True),
              "id": dish_menu.String(description='菜品id',default="201605111052558357"),
              "price": dish_menu.Float(description='菜品原价',default=29.8),
              "num": dish_menu.Integer(description='点菜数量',default=0),
              "guide_image":dish_menu.String(description='图片，基本没有，留着以后用',default="MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5"),
              "name": dish_menu.String(description='菜品名',default="压锅鲤鱼"),
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8)
            }
          ],
          "name": dish_menu.String(description='菜单类别',default="推荐菜")
        },
        {
          "list": [
            {
              "is_discount": dish_menu.Boolean(description='惠标签，是否有优惠',default=True),
              "is_recommend": dish_menu.Boolean(description='推荐标签，是否推荐',default=True),
              "id": dish_menu.String(description='菜品id',default="201605111052558357"),
              "price": dish_menu.Float(description='菜品原价',default=29.8),
              "num": dish_menu.Integer(description='点菜数量',default=0),
              "guide_image":dish_menu.String(description='图片，基本没有，留着以后用',default="MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5"),
              "name": dish_menu.String(description='菜品名',default="压锅鲤鱼"),
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8)
            }
          ],
          "name": dish_menu.String(description='菜单类别',default="酒水")
        }
      ],
  "total": dish_menu.Float(description='总计优惠价格',default=66.6),
  "dish_num": dish_menu.Integer(description='点菜总数量',default=2),
}

}
#点菜菜单
@restaurant_user_api.route('/fm/user/v1/restaurant/dish_menu/',methods=['POST'])
@swag_from(dish_menu.mylpath(schemaid='dish_menu',result=dish_menu_json))
def dish_menu():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                item2 = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':7})
                order_list = []
                for i in item2:
                    if i['preset_dishs'] !=[]:
                        for dish in i['preset_dishs']:
                            order_list.append((dish['id'],dish['num'],dish['discount_price']))
                    if i['preset_wine'] !=[]:
                        for dish in i['preset_wine']:
                            order_list.append((dish['id'],dish['num'],dish['discount_price']))
                data = {}
                list = []
                for i in item:
                    for menu in i['menu']:
                        if menu['dish_type'] == '1' and menu['dishs'] != []:
                            dishjson = {}
                            dishlist = []
                            for dishs in menu['dishs']:
                                dish = {}
                                dish['name'] = dishs['name']
                                dish['price'] = dishs['price']
                                dish['discount_price'] = dishs['discount_price']
                                dish['id'] = dishs['id']
                                dish['is_recommend'] = dishs['is_recommend']
                                if dishs['price'] > dishs['discount_price']:
                                    dish['is_discount'] = True
                                else:
                                    dish['is_discount'] = False
                                dish['guide_image'] = dishs['guide_image']
                                dish['num'] = 0
                                for dishid in order_list:
                                    if dishs['id'] ==dishid[0]:
                                        dish['num'] = dishid[1]
                                dishlist.append(dish)
                            dishjson['list'] = dishlist
                            dishjson['name'] = menu['name']
                            list.append(dishjson)
                dish_num = 0
                total = 0
                for d in order_list:
                    dish_num+=d[1]
                    total+=d[2]
                data['dish_num'] = dish_num
                data['total'] = float("%.2f" % total)
                data['menu'] = list
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
#点菜菜单加减
dish_menu_count = swagger("1-2-3 菜单-2.jpg","点菜菜单加减")
dish_menu_count.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
dish_menu_count.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
dish_menu_count.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
dish_menu_count.add_parameter(name='name',parametertype='formData',type='string',required= True,description='菜品名',default='压锅鲤鱼')
dish_menu_count.add_parameter(name='price',parametertype='formData',type='string',required= True,description='原价',default='29.8')
dish_menu_count.add_parameter(name='discount_price',parametertype='formData',type='string',required= True,description='优惠价',default='29.8')
dish_menu_count.add_parameter(name='type',parametertype='formData',type='string',required= True,description='类别0是菜1是酒',default='0')
dish_menu_count.add_parameter(name='num',parametertype='formData',type='string',required= True,description='数量加减1或-1',default='1')
dish_menu_count.add_parameter(name='id',parametertype='formData',type='string',required= True,description='菜品id',default='201605111052558357')
dish_menu_count_json = {
  "auto": dish_menu_count.String(description='验证是否成功'),
  "message": dish_menu_count.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": dish_menu_count.Integer(description='',default=0),
  "data": {
            "dish_num":dish_menu_count.Integer(description='菜品数量',default=5),
            "total":dish_menu_count.Float(description='总计金额',default=171.4),
}

}
#点菜菜单加减
@restaurant_user_api.route('/fm/user/v1/restaurant/dish_menu_count/',methods=['POST'])
@swag_from(dish_menu_count.mylpath(schemaid='dish_menu_count',result=dish_menu_count_json))
def dish_menu_count():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                pdict = {'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8}
                item2 = mongo.order.find(pdict)

                name = request.form['name']
                price = float(request.form['price'])
                discount_price = float(request.form['discount_price'])
                type = request.form['type']
                num = int(request.form['num'])
                id = request.form['id']

                itemflag = True
                for i in item2:
                    itemflag = False
                if itemflag:
                    json = {
                        "username" : "",
                        "status" : 8,
                        "type" : 1,
                        "source" : 0,
                        "is_room" : True,
                        "restaurant_id" : ObjectId(request.form['restaurant_id']),
                        "preset_dishs" : [],
                        "webuser_id" : ObjectId(request.form['webuser_id']),
                        "phone" : "",
                        "dis_message" : "",
                        "room_id" : "",
                        "deposit" : 0.0,
                        "demand" : "",
                        "total" : 0.0,
                        "numpeople" : 0,
                        "preset_time" : datetime.datetime.now(),
                        "add_time" : datetime.datetime.now(),
                        "preset_wine" : []
                    }
                    mongo.order.insert(json)
                item2 = mongo.order.find(pdict)
                for i in item2:
                    dish_list = []
                    flag = True
                    if type == '0':
                        dishs = i['preset_dishs']
                    else:
                        dishs = i['preset_wine']
                    for dish in dishs:
                        dish_dict = {}
                        if id == dish['id']:
                            flag = False
                            if int(dish['num'])+num != 0:
                                dish_dict['name'] = name
                                dish_dict['price'] = float(request.form['price'])
                                dish_dict['discount_price'] = float(request.form['discount_price'])
                                dish_dict['num'] = int(dish['num'])+num
                                dish_dict['id'] = id
                            else:
                                pass
                        else:
                            dish_dict['name'] = dish['name']
                            dish_dict['price'] = dish['price']
                            dish_dict['discount_price'] = dish['discount_price']
                            dish_dict['num'] = dish['num']
                            dish_dict['id'] = dish['id']
                        if dish_dict != {}:
                            dish_list.append(dish_dict)
                    if flag and num >= 1:
                        dish_list.append(
                            {
                            "name" : name,
                            "price" : float(request.form['price']),
                            "discount_price" : float(request.form['discount_price']),
                            "num" : 1,
                            "id" : id
                            }
                        )
                    print json_util.dumps(dish_list,ensure_ascii=False,indent=2)
                    if type == '0':
                        mongo.order.update_one(pdict,{"$set": {"preset_dishs": dish_list}})
                    else:
                        mongo.order.update_one(pdict,{"$set": {'preset_wine': dish_list}})
                item = mongo.order.find(pdict)
                order_list = []
                for i in item:
                    if i['preset_dishs'] !=[]:
                        for dish in i['preset_dishs']:
                            order_list.append((dish['id'],dish['num'],dish['discount_price']))
                    if i['preset_wine'] !=[]:
                        for dish in i['preset_wine']:
                            order_list.append((dish['id'],dish['num'],dish['discount_price']))
                    dish_num = 0
                    total = 0
                    for d in order_list:
                        dish_num+=d[1]
                        total+=(d[2]*d[1])
                    mongo.order.update_one(pdict,{"$set": {'total': float("%.2f" % total)}})
                    print dish_num,total
                    data = {
                        'dish_num':dish_num,
                        'total':total
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
#我的菜单列表
dish_menu_list = swagger("1-2-3-2 购物车.jpg","我的菜单列表")
dish_menu_list.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
dish_menu_list.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
dish_menu_list_json = {
  "auto": dish_menu_list.String(description='验证是否成功'),
  "message": dish_menu_list.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": dish_menu_list.Integer(description='',default=0),
  "data": {
  "menu": [

    {
      "id": dish_menu_list.String(description='菜单id',default="57aadb1dfb98a45d10b58bda"),
      "total": dish_menu_list.Float(description='总计',default=20.0),
      "r_name": dish_menu_list.String(description='饭店名',default="阿东海鲜老菜馆"),
      "dianfu": dish_menu_list.Float(description='到店支付',default=20.0),
      "deposit": dish_menu_list.Float(description='定金',default=0.0),
      "youhui": dish_menu_list.Float(description='优惠金额',default=1.0),
      "preset_dishs": [
        {
          "id": dish_menu_list.String(description='菜品id',default="201605111053268902"),
          "price": dish_menu_list.Float(description='菜品原价',default=0.0),
          "num": dish_menu_list.Integer(description='数量',default=1),
          "discount_price": dish_menu_list.Float(description='优惠价',default=29.8),
          "name": dish_menu_list.String(description='菜品名',default="小仁鲜"),
        }
      ],
      "preset_wine": [
        {
          "price": dish_menu_list.Float(description='酒水原价',default=4.0),
          "num": dish_menu_list.Integer(description='数量',default=5),
          "discount_price": dish_menu_list.Float(description='优惠价',default=4.0),
          "id": dish_menu_list.String(description='酒水id',default="201605111053577963"),
          "name": dish_menu_list.String(description='酒水名',default="原汁麦"),
        }
      ]
    }
  ]
}

}
#我的菜单列表
@restaurant_user_api.route('/fm/user/v1/restaurant/dish_menu_list/',methods=['POST'])
@swag_from(dish_menu_list.mylpath(schemaid='dish_menu_list',result=dish_menu_list_json))
def dish_menu_list():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item2 = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),'status':8})
                data = {}
                list = []
                for i in item2:
                    json = {}
                    restaurant = mongo.restaurant.find({"_id":i['restaurant_id']})
                    r_name = ''
                    for r in restaurant:
                        r_name = r['name']
                    json['id'] = str(i['_id'])
                    json['r_name'] = r_name
                    json['total'] = i['total']
                    json['deposit'] = i['deposit']
                    json['youhui'] = ''
                    json['dianfu'] = i['total'] - i['deposit']
                    json['preset_dishs'] = i['preset_dishs']
                    json['preset_wine'] = i['preset_wine']
                    json['tishi'] = '提示：再加多少多少元就能免单'
                    if i['preset_dishs'] !=[] or i['preset_wine']!=[]:
                        list.append(json)
                    else:
                        pass
                data['menu'] = list
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
#用户订座
getroom = swagger("1-2-3-3 订座.jpg","用户订座")
getroom.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
getroom.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
getroom.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
getroom.add_parameter(name='username',parametertype='formData',type='string',required= True,description='用户名',default='我叫XXX')
getroom.add_parameter(name='is_room',parametertype='formData',type='string',required= True,description='1是0否选包房',default='0')
getroom.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话',default='13000000000')
getroom.add_parameter(name='demand',parametertype='formData',type='string',required= True,description='需求',default='好吃便宜')
getroom.add_parameter(name='numpeople',parametertype='formData',type='string',required= True,description='用餐人数',default='3')
getroom.add_parameter(name='preset_time',parametertype='formData',type='string',required= True,description='用餐时间',default='2016-08-19 15:15:00')
getroom_json = {
  "auto": getroom.String(description='验证是否成功'),
  "message": getroom.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": getroom.Integer(description='',default=0),
  "data": {
        "status": getroom.Integer(description='访问成功',default=1),
        "msg": getroom.String(description='成功消息',default="订座申请成功")
}

}
#用户订座
@restaurant_user_api.route('/fm/user/v1/restaurant/getroom/',methods=['POST'])
@swag_from(getroom.mylpath(schemaid='getroom',result=getroom_json))
def getroom():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                json = {}
                json['username'] = request.form['username']
                json['status'] = 0
                if request.form['is_room'] == '1':
                    json['is_room'] = True
                else:
                    json['is_room'] = False
                json['phone'] =  request.form['phone']
                json['demand'] =  request.form['demand']
                json['numpeople'] = int( request.form['numpeople'])
                json['preset_time'] = datetime.datetime.strptime(request.form['preset_time'], "%Y-%m-%d %H:%M:%S")
                item = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8})
                flag = True
                for i in item:
                    flag = False
                if flag:
                     json['type'] = 0
                     json['source'] = 2
                     json['restaurant_id'] = ObjectId(request.form['restaurant_id'])
                     json['preset_dishs'] = []
                     json['preset_wine'] = []
                     json['webuser_id'] = ObjectId(request.form['webuser_id'])
                     json['dis_message'] = ""
                     json['room_id'] = ""
                     json['deposit'] = 0.0
                     json['total'] = 0.0
                     json['add_time'] = datetime.datetime.now()
                     mongo.order.insert(json)
                     # tool.tuisong(mfrom=request.form['webuser_id'],
                     #             mto=request.form['restaurant_id'],
                     #             title='美食地图',
                     #             info=mgs_template['sj_1']['title'],
                     #             goto=mgs_template['sj_1']['goto'],
                     #             channel=mgs_template['sj_1']['channel'],
                     #             type='0',
                     #             totype='0',
                     #             appname='foodmap_shop',
                     #             msgtype='message',
                     #             target='all',
                     #             ext='{"goto":'+mgs_template["sj_1"]['goto']+'}',
                     #             ispush=True)
                else:
                    mongo.order.update({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8},{"$set":json})
                    # tool.tuisong(mfrom=request.form['webuser_id'],
                    #              mto=request.form['restaurant_id'],
                    #              title='美食地图',
                    #              info=mgs_template['sj_2']['title'],
                    #              goto=mgs_template['sj_2']['goto'],
                    #              channel=mgs_template['sj_2']['channel'],
                    #              type='0',
                    #              totype='0',
                    #              appname='foodmap_shop',
                    #              msgtype='message',
                    #              target='all',
                    #              ext='{"goto":'+mgs_template["sj_2"]['goto']+'}',
                    #              ispush=True)
                data = {
                    "status": 1,
                    "msg":"订座申请成功"
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
#结算
settlement = swagger("1-2-3-5 收到消息.jpg","结算")
settlement.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
settlement.add_parameter(name='order_id',parametertype='formData',type='string',required= True,description='订单id',default='573153c4e0fdb78f29b42826')
settlement_json = {
  "auto": settlement.String(description='验证是否成功'),
  "message": settlement.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": settlement.Integer(description='',default=0),
  "data": {
          "yingfu": settlement.Float(description='应付金额',default=175.0),
          "room": settlement.String(description='包房名',default="中包（1间）"),
          "r_name": settlement.String(description='饭店名',default="阿东海鲜老菜馆"),
          "preset_dishs": [
            {
              "price": settlement.Float(description='原价',default=29.8),
              "num": settlement.Integer(description='数量',default=1),
              "discount_price": settlement.Float(description='优惠价',default=29.8),
              "id": settlement.String(description='菜品id',default="201605111052558357"),
              "name": settlement.String(description='菜品名',default="压锅鲤鱼")
            }
          ],
          "dianfu": settlement.Float(description='到店付',default=175.0),
          "preset_wine": [
            {
              "price": settlement.Float(description='原价',default=3.0),
              "num": settlement.Integer(description='',default=1),
              "discount_price": settlement.Float(description='优惠价',default=3.0),
              "id": settlement.String(description='菜品id',default="201605111054065811"),
              "name": settlement.String(description='菜品名',default="大雪花"),
            }
          ],
          "numpeople": settlement.Integer(description='用餐人数',default=3),
          "youhui": "",
          "deposit": settlement.Float(description='押金',default=35.0),
          "address": settlement.String(description='饭店地址',default="哈尔滨市南岗区马家街132-2号"),
          "preset_time": settlement.String(description='用餐时间',default="2016年06月24日 14:00:00"),
          "total": settlement.Float(description='总计',default=175.0),
}

}
#结算
@restaurant_user_api.route('/fm/user/v1/restaurant/settlement/',methods=['POST'])
@swag_from(settlement.mylpath(schemaid='settlement',result=settlement_json))
def settlement():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.order.find({'_id':ObjectId(request.form['order_id'])})
                json = {}
                for i in item:
                    restaurant = mongo.restaurant.find({"_id":i['restaurant_id']})
                    r_name = ''
                    room = ''
                    address = ''
                    for r in restaurant:
                        address = r['address']
                        r_name = r['name']
                        for rooms in r['rooms']:
                            if i['room_id'] == rooms['room_id']:
                                room = rooms['room_name']
                    json['r_name'] = r_name
                    json['preset_time'] = i['preset_time'].strftime('%Y年%m月%d日 %H:%M:%S')
                    json['numpeople'] = i['numpeople']
                    json['room'] = room
                    json['address'] = address
                    json['preset_dishs'] = i['preset_dishs']
                    json['preset_wine'] = i['preset_wine']
                    json['total'] = i['total']
                    json['yingfu'] = i['total']
                    json['youhui'] = i['dis_message']
                    json['deposit'] = i['deposit']
                    json['dianfu'] = i['total'] - i['deposit']
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
#联系饭店的电话
getphone = swagger("1-2-3-4 订座提醒.jpg","联系饭店的电话")
getphone.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
getphone.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
getphone_json = {
  "auto": getphone.String(description='验证是否成功'),
  "message": getphone.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": getphone.Integer(description='',default=0),
  "data": {
          "room": getphone.String(description='饭店电话号',default="13000000000")
}

}
#联系饭店的电话
@restaurant_user_api.route('/fm/user/v1/restaurant/getphone/',methods=['POST'])
@swag_from(getphone.mylpath(schemaid='getphone',result=getphone_json))
def getphone():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                phone = ''
                for i in item:
                    phone = i['phone']
                result=tool.return_json(0,"success",True,phone)
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
#单条我的菜单
dish_menu_one = swagger("1-2-3-2 购物车.jpg","单条我的菜单")
dish_menu_one.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
dish_menu_one.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
dish_menu_one.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
dish_menu_one_json = {
  "auto": dish_menu_one.String(description='验证是否成功'),
  "message": dish_menu_one.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": dish_menu_one.Integer(description='',default=0),
  "data": {
  "menu": [

    {
      "id": dish_menu_one.String(description='菜单id',default="57aadb1dfb98a45d10b58bda"),
      "total": dish_menu_one.Float(description='总计',default=20.0),
      "r_name": dish_menu_one.String(description='饭店名',default="阿东海鲜老菜馆"),
      "dianfu": dish_menu_one.Float(description='到店支付',default=20.0),
      "deposit": dish_menu_one.Float(description='定金',default=0.0),
      "youhui": dish_menu_one.Float(description='优惠金额',default=1.0),
      "preset_dishs": [
        {
          "id": dish_menu_one.String(description='菜品id',default="201605111053268902"),
          "price": dish_menu_one.Float(description='菜品原价',default=0.0),
          "num": dish_menu_one.Integer(description='数量',default=1),
          "discount_price": dish_menu_one.Float(description='优惠价',default=29.8),
          "name": dish_menu_one.String(description='菜品名',default="小仁鲜"),
        }
      ],
      "preset_wine": [
        {
          "price": dish_menu_one.Float(description='酒水原价',default=4.0),
          "num": dish_menu_one.Integer(description='数量',default=5),
          "discount_price": dish_menu_one.Float(description='优惠价',default=4.0),
          "id": dish_menu_one.String(description='酒水id',default="201605111053577963"),
          "name": dish_menu_one.String(description='酒水名',default="原汁麦"),
        }
      ]
    }
  ]
}

}
#单条我的菜单
@restaurant_user_api.route('/fm/user/v1/restaurant/dish_menu_one/',methods=['POST'])
@swag_from(dish_menu_one.mylpath(schemaid='dish_menu_one',result=dish_menu_one_json))
def dish_menu_one():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                r_name = ''
                for i in item:
                    r_name = i['name']
                item2 = mongo.order.find({"restaurant_id":ObjectId(request.form['restaurant_id']),'webuser_id':ObjectId(request.form['webuser_id']),'status':8})
                data = {}
                list = []
                for i in item2:
                    json = {}
                    json['id'] = str(i['_id'])
                    json['r_name'] = r_name
                    json['total'] = i['total']
                    json['deposit'] = i['deposit']
                    json['youhui'] = ''
                    json['dianfu'] = i['total'] - i['deposit']
                    json['preset_dishs'] = i['preset_dishs']
                    json['preset_wine'] = i['preset_wine']
                    json['tishi'] = '提示：再加多少多少元免单'
                    if i['preset_dishs'] !=[] or i['preset_wine']!=[]:
                        list.append(json)
                    else:
                        pass
                data['menu'] = list
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
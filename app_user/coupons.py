#--coding:utf-8--#
import random
import time
import pymongo
from flasgger import swag_from

from app_merchant import auto
from tools import tools

import sys

from tools.db_app_user import guess, business_dist, district_list, business_dist_byid, getcoupons, getconcern, checkdish, \
    getxingzhengqu
from tools.message_template import mgs_template
from tools.swagger import swagger

reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime

mongo=conn.mongo_conn()

coupons_user_api = Blueprint('coupons_user_api', __name__, template_folder='templates')

coupons = swagger("3 店粉儿专属优惠.jpg","店粉儿专属优惠")
coupons_json = {
    "auto": coupons.String(description='验证是否成功'),
    "message": coupons.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": coupons.Integer(description='',default=0),
    "data": {
        "list": [
              {
                "wine_discount": coupons.String(description='酒水优惠',default=""),
                "kind3": coupons.String(description='店粉抢优惠',default=""),
                "name": coupons.String(description='饭店名',default="星晨烧烤"),
                "kind1": coupons.String(description='店粉关注即享',default=""),
                "address": coupons.String(description='地址',default="哈尔滨市南岗区平公街7-5号"),
                "id": coupons.String(description='饭店id',default="573542780c1d9b34722f5da9"),
                "guide_image": coupons.String(description='图片',default="09bb491fcde04edd99e898720c3918df"),
                "dishes_discount": coupons.String(description='菜品优惠',default=""),
                "kind2": coupons.String(description='新粉优惠',default=""),
                "concern":coupons.String(description='关注状态0未关注1已关注',default="0"),
              }
    ]
    }
}
coupons.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
coupons.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')
coupons.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='573feadf7c1fa8a326a9c03c')
coupons.add_parameter(name='type',parametertype='formData',type='string',required= True,description='1全部2店粉儿抢特惠',default='1')
@coupons_user_api.route('/fm/user/v1/coupons/coupons/',methods=['POST'])
@swag_from(coupons.mylpath(schemaid='coupons',result=coupons_json))
def coupons():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                type = request.form['type']
                if type == '1':
                    first = {}
                else:
                    rest = mongo.coupons.find({"$or":[{"button":"0"}, {"button":0}],"kind":"3"})
                    r_list = []
                    for i in rest:
                        r_list.append(ObjectId(i['restaurant_id']))
                    first = {"_id":{"$in":r_list}}
                restaurant = mongo.restaurant.find(first).sort("addtime", pymongo.DESCENDING)[star:end]
                list = []
                for rest in restaurant:
                    json = {}
                    for key in rest.keys():
                        if key == '_id':
                            json['id'] = str(rest[key])
                            # json['kind1'] = getcoupons('1',rest[key])['content']
                            # json['kind2'] = getcoupons('2',rest[key])['content']
                            # json['kind3'] = getcoupons('3',rest[key])['content']
                            # json['num'] = getcoupons('3',rest[key])['num']
                            json['kind1'] = '满多少打多少折'
                            json['kind2'] = '满多少减多少元'
                            json['kind3'] = '任性就是送'
                            json['num'] = '1'
                            json['concern'] =getconcern(rest[key],request.form['webuser_id'])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(rest[key])
                        elif key == 'name':
                            json['name'] = rest[key]
                        elif key == 'guanzhu_discount':
                            json['guanzhu_discount'] = rest[key]['message']
                        elif key == 'dishes_discount':
                            json['dishes_discount'] = rest[key]['message']
                        elif key == 'guide_image':
                            json['guide_image'] = rest[key]
                        elif key == 'address':
                            json['address'] = rest[key]
                        elif key == 'wine_discount':
                            json['wine_discount'] = rest[key]['message']
                    list.append(json)
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
#特色名小吃查询类别标签
special_type = swagger("4-1 特色名小吃.jpg","特色名小吃查询类别标签")
special_type.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
special_type_json = {
  "auto": special_type.String(description='验证是否成功'),
  "code": special_type.Integer(description='',default=0),
  "message": special_type.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "data": {
    "business_list": [
      {
        "district_list": {
          "biz_areas": [
            {
              "biz_area_name": special_type.String(description='商圈名',default="腾飞广场"),
              "biz_area_id": special_type.String(description='商圈id',default="13007"),
              "sort": special_type.String(description='排序',default="7"),
              "longitude": special_type.String(description='经度',default="122.535396"),
              "latitude": special_type.String(description='纬度',default="52.977977")
            }
          ]
        },
        "district_id":special_type.String(description='行政区id',default="56d95c1f0f884d3070fbdc4f"),
        "district_name": special_type.String(description='行政区名',default="漠河县"),
      }
    ],
    "fenlei": [
      {
        "id": special_type.String(description='菜系分类id',default="2"),
        "name": special_type.String(description='菜系分类名',default="快餐/小吃")
      },
      {
        "id": special_type.String(description='菜系分类id',default="3"),
        "name": special_type.String(description='菜系分类名',default="烧烤")
      }
    ],
    "youhui": [
      {
        "id": special_type.String(description='菜品优惠',default="dish"),
        "name": special_type.String(description='菜品优惠',default="菜品优惠")
      },
      {
        "id": special_type.String(description='酒水优惠',default="wine"),
        "name": special_type.String(description='酒水优惠',default="酒水优惠")
      },
      {
        "id": special_type.String(description='其他优惠',default="other"),
        "name": special_type.String(description='其他优惠',default="其他优惠")
      }
    ]
  }
}
#特色名小吃查询类别标签
@coupons_user_api.route('/fm/user/v1/coupons/special_type/',methods=['POST'])
@swag_from(special_type.mylpath(schemaid='special_type',result=special_type_json))
def special_type():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                f_list = []
                item = mongo.assortment.find({"parent":{"$in":[1,35,59,50,46]}})
                for i in item:
                    f_json = {}
                    if i['parent'] == 1:
                        f_json['id'] = str(i['_id'])
                        f_json['name'] = i['name']
                        f_list.append(f_json)
                    else:
                        pass
                data['fenlei'] = f_list
                data['youhui'] = [{'id':'dish','name':'菜品优惠'},{'id':'wine','name':'酒水优惠'},{'id':'other','name':'其他优惠'}]
                list = []
                for d in district_list():
                    json = {}
                    json['district_id'] = d['id']
                    json['district_name'] = d['district_name']
                    json['district_list'] = business_dist_byid(d['id'])
                    list.append(json)
                data['business_list'] = list
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

special_restaurant = swagger("4-1 特色名小吃.jpg","列表")
special_restaurant_json = {
    "auto": special_restaurant.String(description='验证是否成功'),
    "message": special_restaurant.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": special_restaurant.Integer(description='',default=0),
    "data": {
        "list": [
              {
                "name": special_restaurant.String(description='饭店名',default="顺兴狗肉"),
                "business_dist": special_restaurant.String(description='商圈名',default="顾乡"),
                "dishes_type": special_restaurant.String(description='菜系',default="炒菜"),
                "hui": special_restaurant.String(description='0没有1有惠标签',default="1"),
                "guide_image": special_restaurant.String(description='饭店头图',default="18d19b3056c5ce33fcf1edc6ffba701c"),
                "district_name": special_restaurant.String(description='行政区名',default="道里区"),
                "id": special_restaurant.String(description='饭店id',default="573413c80c1d9b314998895c"),
              }
        ]
    }
}
special_restaurant.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
special_restaurant.add_parameter(name='business_dist_id',parametertype='formData',type='string',required= True,description='商圈id',default='-1')
special_restaurant.add_parameter(name='district_id',parametertype='formData',type='string',required= True,description='行政区id',default='-1')
special_restaurant.add_parameter(name='dishes_type',parametertype='formData',type='string',required= True,description='菜系',default='-1')
special_restaurant.add_parameter(name='discount',parametertype='formData',type='string',required= True,description='优惠',default='-1')
special_restaurant.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')

#特色名小吃列表
@coupons_user_api.route('/fm/user/v1/coupons/special_restaurant/',methods=['POST'])
@swag_from(special_restaurant.mylpath(schemaid='special_restaurant',result=special_restaurant_json))
def special_restaurant():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                data = {}
                first = {}
                list = []
                #商圈
                if request.form['business_dist_id']!='-1':
                    first["business_dist.id"] = request.form['business_dist_id']
                elif request.form['district_id']!='-1':
                    business_list = []
                    for b in business_dist_byid(request.form['district_id'])['biz_areas']:
                        business_list.append(b['biz_area_id'])
                    first["business_dist.id"] = {"$in":business_list}
                else:
                    pass
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
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                shop_recommend = mongo.shop_recommend.find({"type":2})

                rid_list = []
                for s in shop_recommend:
                    rid_list.append(s['restaurant_id'])
                first['_id'] = {"$in":rid_list}
                item = mongo.restaurant.find(first).sort("addtime", pymongo.DESCENDING)[star:end]
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'name':
                            json['name'] = i[key]
                        elif key == 'guide_image':
                            json['guide_image'] = i[key]
                        elif key == 'business_dist':
                            json['business_dist'] = i[key][0]['name']
                            json['district_name'] = getxingzhengqu(i[key][0]['id'])
                        elif key == 'dishes_type':
                            json['dishes_type'] = i[key][0]['name']
                        else:
                            if i['dishes_discount']['message'] != '':
                                json['hui'] = '1'
                            else:
                                json['hui'] = '0'
                    list.append(json)
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
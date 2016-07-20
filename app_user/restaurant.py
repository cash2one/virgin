#--coding:utf-8--#
import random

import pymongo
from flasgger import swag_from

from app_merchant import auto
from tools import tools
import time
import sys

from tools.db_app_user import guess
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
#饭店列表 条件很多
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant/',methods=['POST'])
def restaurant():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                data = {}
# first = {"dishes_type.id":"10","dishes_discount.message":{"$ne":""},"rooms.room_type.id":"36","tese.id":"54","pay_type.id":{"$in":["48"]},"_id":{"$in":[ObjectId("57329e300c1d9b2f4c85f8e6")]}}
                first = {}
                #分类
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
                #范儿店
                if request.form['recommend']!='-1':
                    pass
                    #
                    if request.form['recommend_type']!='-1':
                        item = mongo.shop_recommend.find({"type":1},{"restaurant_id":1})
                    else:
                        item = mongo.shop_recommend.find({},{"restaurant_id":1})
                    r_idlist = []
                    for i in item:
                        r_idlist.append(i['restaurant_id'])
                    first['_id'] = {"$in":r_idlist}
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                list = guess(first=first,lat1=float(request.form['x']),lon1=float(request.form['y']),start=star,end=end)
                data['list'] = list
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",False,None)
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
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#饭店查询类别标签
restaurant_type = swagger("订单","餐位管理")
restaurant_type.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
rjson={
  "auto": restaurant_type.String(description='验证是否成功'),
  "code": restaurant_type.Integer(description='',default=0),
  "date": {
      "fenlei": [
      {
        "id": "2",
        "name": "快餐/小吃"
      },
      {
        "id": "3",
        "name": "烧烤"
      },
      {
        "id": "4",
        "name": "火锅"
      },
      {
        "id": "5",
        "name": "铁锅炖"
      },
      {
        "id": "6",
        "name": "川菜/湘菜"
      },
      {
        "id": "7",
        "name": "海鲜"
      },
      {
        "id": "8",
        "name": "烤肉"
      },
      {
        "id": "9",
        "name": "粤菜/茶餐厅"
      },
      {
        "id": "10",
        "name": "炒菜"
      },
      {
        "id": "11",
        "name": "清真"
      },
      {
        "id": "12",
        "name": "面包/甜点"
      },
      {
        "id": "13",
        "name": "韩餐/狗肉"
      },
      {
        "id": "14",
        "name": "日本料理"
      },
      {
        "id": "15",
        "name": "鱼锅"
      },
      {
        "id": "16",
        "name": "斋"
      },
      {
        "id": "17",
        "name": "筋饼"
      },
      {
        "id": "18",
        "name": "汤/粥/养生"
      },
      {
        "id": "19",
        "name": "西餐"
      },
      {
        "id": "20",
        "name": "包子/饺子"
      },
      {
        "id": "21",
        "name": "烤鱼"
      },
      {
        "id": "22",
        "name": "东南亚菜"
      },
      {
        "id": "23",
        "name": "熏酱"
      },
      {
        "id": "24",
        "name": "小龙虾"
      },
      {
        "id": "25",
        "name": "自助"
      },
      {
        "id": "26",
        "name": "其它"
      },
      {
        "id": "27",
        "name": "西餐"
      },
      {
        "id": "28",
        "name": "斋"
      }
    ],
    "youhui": [
      {
        "id": "dish",
        "name": "菜品优惠"
      },
      {
        "id": "wine",
        "name": "酒水优惠"
      },
      {
        "id": "other",
        "name": "其他优惠"
      }
    ],
    "tese": [
      {
        "id": "51",
        "name": "演艺"
      },
      {
        "id": "52",
        "name": "24小时营业"
      },
      {
        "id": "53",
        "name": "停车场"
      },
      {
        "id": "54",
        "name": "WiFi"
      }
    ],
    "zhifu": [
      {
        "id": "47",
        "name": "刷卡支付"
      },
      {
        "id": "48",
        "name": "微信支付"
      },
      {
        "id": "49",
        "name": "支付宝支付"
      }
    ],
    "baofang": [
      {
        "id": "36",
        "name": "带洗手间包房"
      }
    ]
  },
  "message": restaurant_type.String(description='',default="")
}
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_type/',methods=['POST'])
@swag_from(restaurant_type.mylpath(schemaid='orderbypreset',result=rjson))
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
                    elif i['parent'] == 35 or i['parent'] == 59:
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
                result=tool.return_json(0,"field",True,e)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)

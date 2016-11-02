#--coding:utf-8--#
import random
import time
import pymongo
from flasgger import swag_from

from app_merchant import auto
from app_user.groupinvite import GroupInvite
from tools import tools

import sys

from tools.db_app_user import guess, business_dist, district_list, business_dist_byid, getcoupons, getconcern, checkdish, \
    coupons_by, use_coupons, getimg, hobby
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
import connect.settings as settings
mongo=conn.mongo_conn()

restaurant_user_api = Blueprint('restaurant_user_api', __name__, template_folder='templates')


index = swagger("0 首页改.jpg","首页接口（不含搜索和猜你喜欢，这两块单写）")
index_json = {
    "auto": index.String(description='验证是否成功'),
    "message": index.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": index.Integer(description='',default=0),
    "data": {
        "kaituan": [
          {
            "pic": index.String(description='图片md5',default="2884eec3c74aebef5e7517cc78699d36"),
            "old_price": index.Float(description='原价',default=200.0),
            "detail": index.String(description='详情描述',default="详情描述"),
            "time_range": index.String(description='时间',default="10:30"),
            "restaurant_name": index.String(description='饭店名',default="10号熏酱骨头馆"),
            "now_price": index.Float(description='现价',default=122.0),
            "size":index.Integer(description='人数',default=4)
          }
        ],
        # "guess": [],
        "img": {
          "img": index.String(description='店粉优惠图',default="ce3e93a981520f9085dd83e0e8fa880b"),
          "title": index.String(description='标题',default="标题")
        },
        "coupons": [
          {
            "rest_name": index.String(description='饭店名',default="饭店名"),
            "img": index.String(description='图片md5',default="b0040dfcbf2a70d91c7e364ea6c1bf7b"),
            "id2": index.String(description='优惠id',default="5783098c7c1fa4826dce8fbf"),
            "id3": index.String(description='优惠id',default="578309097c1fa4826dce8fbb"),
            "id1": index.String(description='优惠id',default="5783097b7c1fa4826dce8fbd"),
            "title1": index.String(description='优惠标题',default="全品满100.0元打0.8折"),
            "title2": index.String(description='优惠标题',default="全品满100.0元减30.0元"),
            "title3": index.String(description='优惠标题',default="下单即减40.0元"),
          }
        ],
        "recommend": {
          "content": index.String(description='内容',default="内容"),
          "dishs": [
            {
              "dishs_summary": index.String(description='菜品概括',default="菜品概括"),
              "id": index.String(description='菜品id',default="201608111433153294"),
              "dishs_img": index.String(description='菜品id',default="菜品图"),
              "name": index.String(description='菜品名',default="肉炒白菜木耳"),
            }
          ],
          "restaurant_id": index.String(description='饭店id',default="57329f790c1d9b2f3e5dfbab"),
          "restaurant_name": index.String(description='饭店名',default="八福熏酱"),
          "id": index.String(description='范儿店id',default="57a974ef612c5e193c559604")
        }
    }
}
index.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/index/',methods=['POST'])
@swag_from(index.mylpath(schemaid='index',result=index_json))
def index():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            # try:
                data = {}
                #轮换图 开始
                imglist = []
                turnsimg = mongo.turnsimg.find({"appid":"3"})
                for t in turnsimg:
                    data['turnsimg'] = t['huodong']
                #轮换图结束
                #开团请客 开始
                kaituan = GroupInvite().all_item
                list = []
                for k in kaituan:
                    json = {}
                    json['detail'] = k['detail']
                    json['restaurant_name'] = k['restaurant']['name']
                    json['restaurant_id'] = k['restaurant']['rid']
                    json['size'] = k['group_info']['size']
                    json['old_price'] = k['price']['old']
                    json['now_price'] = k['price']['now']
                    json['pic'] = k['restaurant']['pic']
                    json['time_range'] = k['time_range']
                    list.append(json)
                data['kaituan'] = list[0:4]
                #开团请客 结束
                #店粉优惠 随机两个饭店 开始
                count = len(mongo.coupons.distinct('restaurant_id',{'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()},"button":"0"}))
                if count>=2:
                    randomnum = random.randint(0, count-2)
                else:
                    randomnum = 0
                restaurant_id = mongo.coupons.distinct('restaurant_id',{'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()},"button":"0"})[randomnum:randomnum+2]
                idlist = []
                for i in restaurant_id:
                    idlist.append(i)
                coupons = {}
                couponslist = []
                num = 0
                for i in idlist:
                    rest = mongo.restaurant.find({"_id":ObjectId(idlist[num])})
                    for r in rest:
                        coupons['rest_name'] = r['name']
                        coupons['rest_id'] = str(r['_id'])
                    coupons['title1'] = getcoupons('1',idlist[num])['content']
                    coupons['id1'] = getcoupons('1',idlist[num])['id']
                    coupons['title2'] = getcoupons('2',idlist[num])['content']
                    coupons['id2'] = getcoupons('2',idlist[num])['id']
                    coupons['title3'] = getcoupons('3',idlist[num])['content']
                    coupons['id3'] = getcoupons('3',idlist[num])['id']
                    coupons['img'] = getimg(idlist[num])
                    num+=1
                    couponslist.append(coupons)
                data['coupons'] = couponslist
                #店粉优惠 随机两个饭店 结束
                #店粉优惠专用图片 开始
                image = mongo.img.find()
                imgjson = {}
                for img in image:
                    imgjson['img'] = img['img']
                    imgjson['title'] = img['title']
                data['img'] = imgjson
                #店粉优惠专用图片 结束
                #今日范儿店 开始
                shop_recommend = mongo.shop_recommend.find({'type':2}).sort("addtime", pymongo.DESCENDING)[0:1]
                recommend = {}
                for i in shop_recommend:

                    for key in i.keys():
                        if key == '_id':
                            recommend['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            recommend['restaurant_id'] = str(i[key])
                        elif key == 'restaurant_name':
                            recommend['restaurant_name'] = i[key]
                        elif key == 'summary':
                            recommend['content'] = i[key]
                        elif key == 'dishs':
                            recommend['dishs'] = i[key][0:3]
                        elif key == 'headimage':
                            recommend['headimage'] = i[key]
                        else:
                            pass
                data['recommend'] = recommend
                #今日范儿店 结束
                #猜你喜欢 开始
                guesslist = []
                data['guess'] = guesslist
                #猜你喜欢 结束
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"success",False,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)

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
restaurant.add_parameter(name='dishes_type',parametertype='formData',type='string',required= True,description='菜系',default='10')
restaurant.add_parameter(name='discount',parametertype='formData',type='string',required= True,description='优惠',default='dish')
restaurant.add_parameter(name='room_people_id',parametertype='formData',type='string',required= True,description='包房id',default='40')
restaurant.add_parameter(name='room_type',parametertype='formData',type='string',required= True,description='包房特色',default='36')
restaurant.add_parameter(name='tese',parametertype='formData',type='string',required= True,description='特色',default='51')
restaurant.add_parameter(name='pay_type',parametertype='formData',type='string',required= True,description='支付',default='48')
restaurant.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')
restaurant.add_parameter(name='x',parametertype='formData',type='string',required= True,description='经度坐标x，没有传x',default='126.62687122442075')
restaurant.add_parameter(name='y',parametertype='formData',type='string',required= True,description='纬度坐标y，没有传y',default='45.764067772341264')
restaurant.add_parameter(name='business_dist_id',parametertype='formData',type='string',required= True,description='商圈id',default='-1')
restaurant.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id,未登录传-1',default='57396ec17c1f31a9cce960f4')
#饭店列表 条件很多
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/restaurant/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/restaurant_img/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/restaurant_type/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/getbusiness_dist/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/getdistrict_list/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/getbusiness_dist_byid/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/concern/',methods=['POST'])
@swag_from(concern.mylpath(schemaid='concern',result=concern_json))
def concern():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                restaurant_id = request.form['restaurant_id']
                webuser_id = request.form['webuser_id']
                data = {
                    "restaurant_id" : ObjectId(restaurant_id),
                    "webuser_id" : ObjectId(webuser_id),
                    "addtime" : datetime.datetime.now()
                }
                item = mongo.concern.find({"restaurant_id" : ObjectId(restaurant_id),"webuser_id" : ObjectId(webuser_id)})
                flag = True
                for i in item:
                    flag = False
                if flag:
                    mycoupons = mongo.mycoupons.find({"restaurant_id":ObjectId(restaurant_id),"webuser_id" : ObjectId(webuser_id),"kind":"2"})
                    m_flag = True
                    for m in mycoupons:
                        m_flag = False
                    coupons = coupons_by({"restaurant_id":ObjectId(restaurant_id),"kind":"2","$or":[{"button":"0"}, {"button":0}]})
                    if coupons and m_flag:
                        restaurant = mongo.restaurant.find({"_id":ObjectId(restaurant_id)})
                        for i in restaurant:
                            json = {
                                "restaurant_id" : ObjectId(restaurant_id),
                                "guide_image":i['guide_image'],
                                "webuser_id" : ObjectId(webuser_id),
                                "coupons_id" : ObjectId(coupons['id']),
                                "status" : "1",
                                "kind" : "2",
                                "r_name" : i['name'],
                                "address" : i['address'],
                                "phone" : i['phone'],
                                "content" : coupons['content'],
                                "expiry_date" : coupons['indate_start']+"-"+coupons['indate_end'],
                                "role" : coupons['rulename'],
                                "indate_start" : datetime.datetime.strptime("1980-01-01", "%Y-%m-%d"),
                                "indate_end" : datetime.datetime.strptime("2100-01-01", "%Y-%m-%d"),
                            }
                            mongo.mycoupons.insert(json)
                    mongo.concern.insert(data)
                    json = {
                            "status": 1,
                            "concern":"1"
                    }
                else:
                    mongo.concern.remove({"restaurant_id" : ObjectId(restaurant_id),"webuser_id" : ObjectId(webuser_id)})
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
          "guanzhu": restaurant_info.String(description='关注优惠',default="关注优惠"),
          "xinfener": restaurant_info.String(description='新粉儿优惠',default="新粉儿优惠"),
          "kaituan": restaurant_info.String(description='开团请客',default="开团请客"),
          "concern": restaurant_info.String(description='是否关注1是0否',default="1")
    }
}
#饭店详情
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/restaurant_info/',methods=['POST'])
@swag_from(restaurant_info.mylpath(schemaid='restaurant_info',result=restaurant_info_json))
def restaurant_info():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                webuser_id = request.form['webuser_id']
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                data = {}
                for i in item:
                    data['id'] = str(i['_id'])
                    data['zc1'] = i['zc1']
                    data['zc2'] = i['zc2']
                    data['show_photos'] = {"img": i['guide_image'],"desc": ""}
                    if i['show_photos'] != []:
                        data['photos_num'] = tool.pic_num(request.form['restaurant_id'])
                    else:
                        data['show_photos'] = {"img": "","desc": ""}
                        data['photos_num'] = 0
                    data['name'] = i['name']
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
                        wine_discount = '酒水'+str(i['wine_discount']['discount']*10)+'折,'
                    wine_discount += i['wine_discount']['message']
                    data['wine_discount'] =wine_discount
                    data['coupons'] =getcoupons('3',str(i['_id']))
                    data['guanzhu'] =getcoupons('1',str(i['_id']))['content']
                    data['xinfener'] =getcoupons('2',str(i['_id']))['content']
                    #开团请客（暂时空着）
                    kaituan = mongo.qingke.find({"nid":request.form["restaurant_id"]}).sort("time", pymongo.DESCENDING)[0:1]
                    data['kaituan'] = ''
                    for k in kaituan:
                        data['kaituan'] = k['nr']+"人开团请客，原价"+k['zj']+"元，现价"+k['price']+"元"
                    data['concern'] = getconcern(str(i['_id']),webuser_id)
                    data['address'] = i['address']
                    data['phone'] = i['phone']
                    data['open'] = i['open']
                    data['yanyi'] = '无'
                    data['24xiaoshi'] = '无'
                    data['tingchechang'] = '无'
                    data['WiFi'] = '无'
                    for tese in i['tese']:
                        data['yanyi'] = '有' if '51' == tese['id'] else '无'
                        data['24xiaoshi'] = '有' if '52' == tese['id'] else '无'
                        data['tingchechang'] = '有' if '53' == tese['id'] else '无'
                        data['WiFi'] = '有' if '54' == tese['id'] else '无'
                    data['shuaka'] = '0'
                    data['weixin'] = '0'
                    data['zhifubao'] = '0'
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
                    data['tuijiancai'] =''
                    for menu in  i['menu']:
                        if menu['name'] == '推荐菜':
                            data['tuijiancai'] = menu['dishs']
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",True,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#图片菜单
pic_menu = swagger("1-2-3 菜单-1.jpg","图片菜单")
pic_menu.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
pic_menu.add_parameter(name='type',parametertype='formData',type='string',required= True,description='标签分类4全部图片5推荐菜6酒水',default='4')
pic_menu.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='57329e300c1d9b2f4c85f8e6')
pic_menu_json = {
  "auto": pic_menu.String(description='验证是否成功'),
  "message": pic_menu.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": pic_menu.Integer(description='',default=0),
  "data": {
  "list": [
                  {
                    "img": pic_menu.String(description='图片MD5',default="015a0f05de8146a45c0681ba64bc49f6"),
                    "desc": pic_menu.String(description='排序，这个真没有',default="")
                  },
                  {
                    "img": pic_menu.String(description='图片MD5',default="f71d4db90411bd4c598821a72aa217bb"),
                    "desc": pic_menu.String(description='排序，这个真没有',default="")
                  }
      ],
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/pic_menu/',methods=['POST'])
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
                    plist = []
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
                    if type == '4':
                        for pic in piclist:
                            picjson = {
                                'desc':'',
                                'img':pic
                            }
                            plist.append(picjson)
                        data['list'] = plist
                    elif type == '5':
                        data['tuijiancai'] = tuijiancaislist
                    elif type == '6':
                        data['wine'] = winelist
                    else:
                        pass
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
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8),
              "type": dish_menu.String(description='0酒水1菜品',default="1"),
            },
            {
              "is_discount": dish_menu.Boolean(description='惠标签，是否有优惠',default=True),
              "is_recommend": dish_menu.Boolean(description='推荐标签，是否推荐',default=True),
              "id": dish_menu.String(description='菜品id',default="201605111052558357"),
              "price": dish_menu.Float(description='菜品原价',default=29.8),
              "num": dish_menu.Integer(description='点菜数量',default=0),
              "guide_image":dish_menu.String(description='图片，基本没有，留着以后用',default="MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5MD5"),
              "name": dish_menu.String(description='菜品名',default="压锅鲤鱼"),
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8),
              "type": dish_menu.String(description='0酒水1菜品',default="1"),
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
              "discount_price":dish_menu.Float(description='菜品优惠价',default=29.8),
              "type": dish_menu.String(description='1酒水0菜品',default="0"),
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/dish_menu/',methods=['POST'])
@swag_from(dish_menu.mylpath(schemaid='dish_menu',result=dish_menu_json))
def dish_menu():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                item2 = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8})
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
                                if menu['name'] == '酒水':
                                    dish['type'] = '1'
                                else:
                                    dish['type'] = '0'
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/dish_menu_count/',methods=['POST'])
@swag_from(dish_menu_count.mylpath(schemaid='dish_menu_count',result=dish_menu_count_json))
def dish_menu_count():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                pdict = {'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8}
                item2 = mongo.order.find(pdict)

                name = request.form['name']
                type = request.form['type']
                num = int(request.form['num'])
                id = request.form['id']

                itemflag = True
                for i in item2:
                    itemflag = False
                if itemflag:
                    json = {
                        "order_id":"MSDT%s%03d" % (int(time.time() * 1000), random.randint(1, 999)),
                        "username" : "",
                        "status" : 8,
                        "type" : 1,
                        "source" : 0,
                        "is_room" : True,
                        "restaurant_id" : ObjectId(request.form['restaurant_id']),
                        "preset_dishs" : [],
                        "webuser_id" : ObjectId(request.form['webuser_id']),
                        "phone" : "",
                        "dis_message" : [{
                                "dis_type":"",
                                "content":"",
                                "coupons_id":"",
                                "dis_amount":""
                            }],
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
                    # print json_util.dumps(dish_list,ensure_ascii=False,indent=2)
                    if type == '0':
                        mongo.order.update_one(pdict,{"$set": {"preset_dishs": dish_list}})
                    else:
                        mongo.order.update_one(pdict,{"$set": {'preset_wine': dish_list}})
                item = mongo.order.find(pdict)
                dish_list = []
                wine_list = []
                for i in item:
                    if i['preset_dishs'] !=[]:
                        for dish in i['preset_dishs']:
                            dish_list.append((dish['id'],dish['num'],dish['discount_price']))
                    if i['preset_wine'] !=[]:
                        for dish in i['preset_wine']:
                            wine_list.append((dish['id'],dish['num'],dish['discount_price']))

                    wine_num = 0
                    dish_num = 0
                    dish_total = 0
                    wine_total = 0
                    for d in dish_list:
                        dish_num+=d[1]
                        dish_total+=(d[2]*d[1])
                    for w in wine_list:
                        wine_num+=w[1]
                        wine_total+=(w[2]*w[1])
                    total = wine_total+dish_total
                    order_num = wine_num+dish_num
                    print wine_num,dish_num,dish_total,wine_total
                    mycoupons = use_coupons(total = total,dish_total = dish_total,wine_total = wine_total,restaurant_id=request.form['restaurant_id'],webuser_id=request.form['webuser_id'])
                    dis_message = []
                    deposit = 0.0
                    if mycoupons:
                        for m in mycoupons[1]:
                            deposit+=m[0]
                            coupons = mongo.coupons.find({"_id":ObjectId(m[4])})
                            for c in coupons:
                                content = ''
                                if c['type'] == '1':
                                    if c['rule'] == '0':
                                        content = '下单即减'+str(c['cross-claim'])+'元'
                                    elif c['rule'] == '1':
                                        content = '全品满'+str(c['money'])+'元即减'+str(c['cross-claim'])+'元'
                                    elif c['rule'] == '2':
                                        content = '菜品满'+str(c['money'])+'元即减'+str(c['cross-claim'])+'元'
                                    elif c['rule'] == '3':
                                        content = '酒类满'+str(c['money'])+'元即减'+str(c['cross-claim'])+'元'
                                    else:
                                        pass
                                elif c['type'] == '2':
                                    if c['rule'] == '0':
                                        content = '下单即打'+str(c['cross-claim'])+'折'
                                    elif c['rule'] == '1':
                                        content = '全品满'+str(c['money'])+'元即打'+str(c['cross-claim'])+'折'
                                    elif c['rule'] == '2':
                                        content = '菜品满'+str(c['money'])+'元即打'+str(c['cross-claim'])+'折'
                                    elif c['rule'] == '3':
                                        content = '酒类满'+str(c['money'])+'元即打'+str(c['cross-claim'])+'折'
                                    else:
                                        pass
                                else:
                                    pass
                                dis_message.append(
                                    {
                                        "dis_type":c['kind'],
                                        "content":content,
                                        "coupons_id":str(c['_id']),
                                        "dis_amount":float("%.2f" % m[0])
                                    }
                                )
                    mongo.order.update_one(pdict,{"$set": {'deposit':float("%.2f" % deposit),'dis_message':dis_message,'total': float("%.2f" % total)}})
                    data = {
                        'dish_num':order_num,
                        'total':float("%.2f" % total)
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/dish_menu_list/',methods=['POST'])
@swag_from(dish_menu_list.mylpath(schemaid='dish_menu_list',result=dish_menu_list_json))
def dish_menu_list():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                checkdish(request.form['webuser_id'])
                item2 = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),'status':8})
                data = {}
                list = []
                dish_list = []
                wine_list = []
                for i in item2:
                    if i['preset_dishs'] !=[]:
                        for dish in i['preset_dishs']:
                            dish_list.append((dish['id'],dish['num'],dish['discount_price']))
                    if i['preset_wine'] !=[]:
                        for dish in i['preset_wine']:
                            wine_list.append((dish['id'],dish['num'],dish['discount_price']))
                    dish_total = 0
                    wine_total = 0
                    for d in dish_list:
                        dish_total+=(d[2]*d[1])
                    for w in wine_list:
                        wine_total+=(w[2]*w[1])
                    total = wine_total+dish_total
                    print dish_total,wine_total,i['restaurant_id'],request.form['webuser_id']
                    mycoupons = use_coupons(total = total,dish_total = dish_total,wine_total = wine_total,restaurant_id=str(i['restaurant_id']),webuser_id=request.form['webuser_id'])
                    print mycoupons
                    json = {}
                    restaurant = mongo.restaurant.find({"_id":i['restaurant_id']})
                    r_name = ''
                    for r in restaurant:
                        r_name = r['name']
                    json['id'] = str(i['_id'])
                    json['r_name'] = r_name
                    json['total'] = i['total']
                    json['deposit'] = i['deposit']
                    y_list = []
                    dis_amounts = 0.0
                    for dis in i['dis_message']:
                        dis_amounts+=dis['dis_amount']
                        if dis['dis_type'] == '1':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'关注即享:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'关注即享:',
                                'second':str(dis['dis_amount'])
                            })
                        elif dis['dis_type'] == '2':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'新粉优惠:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'新粉优惠:',
                                'second':str(dis['dis_amount'])
                            })
                        elif dis['dis_type'] == '3':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'店粉抢优惠:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'店粉抢优惠:',
                                'second':str(dis['dis_amount'])
                            })
                        else:
                            pass
                    json['youhui'] = y_list
                    json['yingfu'] =str(i['total'] - dis_amounts)
                    json['yajin'] = '100'
                    json['dianfu'] = '200'
                    json['preset_dishs'] = i['preset_dishs']
                    json['preset_wine'] = i['preset_wine']
                    json['tishi'] = mycoupons[0]
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/getroom/',methods=['POST'])
@swag_from(getroom.mylpath(schemaid='getroom',result=getroom_json))
def getroom():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                json = {}
                json['username'] = request.form['username']
                json['status'] = 0
                is_room = '大厅'
                if request.form['is_room'] == '1':
                    json['is_room'] = True
                    is_room = '包房'
                else:
                    json['is_room'] = False
                json['phone'] =  request.form['phone']
                json['demand'] =  request.form['demand']
                json['numpeople'] = int( request.form['numpeople'])
                json['preset_time'] = datetime.datetime.strptime(request.form['preset_time'], "%Y-%m-%d %H:%M:%S")
                content = '联系人：'+request.form['username']+'，联系电话：'+request.form['phone']+\
                          '，用餐人数：'+request.form['numpeople']+'，包房/大厅：'+is_room+'，时间：'+\
                          request.form['preset_time']+'，要求：'+request.form['demand']+'。'
                item = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8})
                flag = True
                for i in item:
                    flag = False
                if flag:
                     json['order_id'] = "MSDT%s%03d" % (int(time.time() * 1000), random.randint(1, 999)),
                     json['type'] = 0
                     json['source'] = 2
                     json['restaurant_id'] = ObjectId(request.form['restaurant_id'])
                     json['preset_dishs'] = []
                     json['preset_wine'] = []
                     json['webuser_id'] = ObjectId(request.form['webuser_id'])
                     json['dis_message'] = {
                        "dis_type":"",
                        "content":"",
                        "coupons_id":"",
                        "dis_amount":""
                    },
                     json['room_id'] = ""
                     json['deposit'] = 0.0
                     json['total'] = 0.0
                     json['add_time'] = datetime.datetime.now()
                     orderid = mongo.order.insert(json)
                     #推送1 /fm/merchant/v1/order/orderinfos/
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                     tool.tuisong(mfrom=request.form['webuser_id'],
                                 mto=request.form['restaurant_id'],
                                 title='您有一条新的订座消息',
                                 info=content,
                                 goto='1',
                                 channel='订座',
                                 type='0',
                                 totype='0',
                                 appname='foodmap_shop',
                                 msgtype='notice',
                                 target='device',
                                 ext='{"goto":"1","id":"'+str(orderid)+'"}',
                                 ispush=True)
                else:
                    mongo.order.update({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8},{"$set":json})
                    myorder = mongo.order.find({'webuser_id':ObjectId(request.form['webuser_id']),"restaurant_id":ObjectId(request.form['restaurant_id']),'status':8})
                    orderid = ''
                    for o in myorder:
                        orderid = o['_id']
                    #推送2 /fm/merchant/v1/order/orderinfos/
                    tool.tuisong(mfrom=request.form['webuser_id'],
                                 mto=request.form['restaurant_id'],
                                 title='您有一条新的点菜消息',
                                 info=content,
                                 goto='2',
                                 channel='点菜',
                                 type='0',
                                 totype='0',
                                 appname='foodmap_shop',
                                 msgtype='notice',
                                 target='device',
                                 ext='{"goto":"1","id":"'+str(orderid)+'"}',
                                 ispush=True)
                data = {
                    "status": 1,
                    "msg":"订座申请成功"
                }
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",True,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
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
          "youhui": [
                    {
                "content" : settlement.String(description='优惠描述',default="全品满100.0元即打0.8折"),
                "coupons_id" : settlement.String(description='优惠id',default="5783097b7c1fa4826dce8fbd"),
                "dis_type" : settlement.String(description='优惠类别1现金2折扣',default="1"),
                "dis_amount" : settlement.Float(description='优惠金额',default=205.64),
            },
          ],
          "deposit": settlement.Float(description='押金',default=35.0),
          "address": settlement.String(description='饭店地址',default="哈尔滨市南岗区马家街132-2号"),
          "preset_time": settlement.String(description='用餐时间',default="2016年06月24日 14:00:00"),
          "total": settlement.Float(description='总计',default=175.0),
}

}
#结算
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/settlement/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/getphone/',methods=['POST'])
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
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/dish_menu_one/',methods=['POST'])
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
                dish_list = []
                wine_list = []
                for i in item2:
                    if i['preset_dishs'] !=[]:
                        for dish in i['preset_dishs']:
                            dish_list.append((dish['id'],dish['num'],dish['discount_price']))
                    if i['preset_wine'] !=[]:
                        for dish in i['preset_wine']:
                            wine_list.append((dish['id'],dish['num'],dish['discount_price']))
                    dish_total = 0
                    wine_total = 0
                    for d in dish_list:
                        dish_total+=(d[2]*d[1])
                    for w in wine_list:
                        wine_total+=(w[2]*w[1])
                    total = wine_total+dish_total
                    print dish_total,wine_total,i['restaurant_id'],request.form['webuser_id']
                    mycoupons = use_coupons(total = total,dish_total = dish_total,wine_total = wine_total,restaurant_id=str(i['restaurant_id']),webuser_id=request.form['webuser_id'])
                    print mycoupons
                    json = {}
                    json['id'] = str(i['_id'])
                    json['r_name'] = r_name
                    json['total'] = i['total']
                    json['deposit'] = i['deposit']
                    y_list = []
                    dis_amounts = 0.0
                    for dis in i['dis_message']:
                        dis_amounts+=dis['dis_amount']
                        if dis['dis_type'] == '1':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'关注即享:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'关注即享:',
                                'second':str(dis['dis_amount'])
                            })
                        elif dis['dis_type'] == '2':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'新粉优惠:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'新粉优惠:',
                                'second':str(dis['dis_amount'])
                            })
                        elif dis['dis_type'] == '3':
                            y_list.append({
                                'msg':'<font size=\"3\">'+'店粉抢优惠:'+'<font size=\"3\" color=\"red\">'+str(dis['dis_amount'])+'元</font></font>',
                                'first':'店粉抢优惠:',
                                'second':str(dis['dis_amount'])
                            })
                        else:
                            pass
                    json['youhui'] = y_list
                    json['yingfu'] =str(i['total'] - dis_amounts)
                    json['yajin'] = '100'
                    json['dianfu'] = '200'
                    json['preset_dishs'] = i['preset_dishs']
                    json['preset_wine'] = i['preset_wine']
                    json['tishi'] = mycoupons[0]
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
#连锁店
liansuo = swagger("1-1-1 连锁店列表.jpg","连锁店列表")
liansuo.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
liansuo.add_parameter(name='district_id',parametertype='formData',type='string',required= True,description='行政区id,初始传-1',default='56d7af296bff8928c07855dc')
liansuo.add_parameter(name='restaurant_id',parametertype='formData',type='string',required= True,description='饭店id',default='573ad312612c5e0a6078f416')
liansuo_json = {
  "auto": liansuo.String(description='验证是否成功'),
  "message": liansuo.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": liansuo.Integer(description='',default=0),
  "data": {
    "list":[
        {
            "id":liansuo.String(description='饭店id',default="57329e300c1d9b2f4c85f8e6"),
            "name":liansuo.String(description='饭店名',default="1981只是一家串店"),
            "address":liansuo.String(description='地址',default="哈尔滨市南岗区花园街201号"),
            "phone":liansuo.String(description='电话',default="0451-12345678"),
        }
    ]
}

}
#连锁店列表
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/liansuo/',methods=['POST'])
@swag_from(liansuo.mylpath(schemaid='liansuo',result=liansuo_json))
def liansuo():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                data = {}
                list = []
                fendian = ''

                restaurant = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                for rest in restaurant:
                    if 'id' in rest['fendian'].keys():
                        fendian = rest['fendian']['id']
                    else:
                        fendian = ""
                if request.form['district_id'] !='-1':
                    dist_list = []
                    district = mongo.district.find({"_id":ObjectId(request.form['district_id'])})
                    for dist in district:
                        for biz in dist['biz_areas']:
                            dist_list.append(str(biz['biz_area_id']))
                    first = {"fendian.id":fendian,"business_dist.id":{"$in":dist_list}}
                else:
                    first = {"fendian.id":fendian}
                item = mongo.restaurant.find(first)
                for i in item:
                    json = {
                        "id":str(i['_id']),
                        "name":i['name'],
                        "address":i['address'],
                        "phone":i['phone']
                    }
                    list.append(json)
                data['list'] = list
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",True,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#首页搜索
search = swagger("0 首页改.jpg","首页搜索")
search.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
search.add_parameter(name='str',parametertype='formData',type='string',required= True,description='饭店名',default='饭店')
search_json = {
  "auto": search.String(description='验证是否成功'),
  "message": search.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": search.Integer(description='',default=0),
  "data": {
        "list":[
            {
                "id":search.String(description='id',default="id"),
                "name":search.String(description='name',default="name")
            }
        ]
}

}
#首页搜索
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/search/',methods=['POST'])
@swag_from(search.mylpath(schemaid='search',result=search_json))
def search():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                list = []
                restaurant = mongo.restaurant.find({"name":{"$regex":request.form['str']}})
                for rest in restaurant:
                    json = {}
                    json['name'] = rest['name']
                    json['id'] = str(rest['_id'])
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
#猜你喜欢
hobbys = swagger("0 首页改.jpg","猜你喜欢")
hobbys.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
hobbys.add_parameter(name='lon',parametertype='formData',type='string',required= True,description='经度',default='126.65381534034498')
hobbys.add_parameter(name='lat',parametertype='formData',type='string',required= True,description='纬度',default='45.76196769636328')
hobbys_json = {
  "auto": hobbys.String(description='验证是否成功'),
  "message": hobbys.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": hobbys.Integer(description='',default=0),
  "data": {
        "list": [
      {
        "distance":  hobbys.Integer(description='',default=993),
        "wine_discount": hobbys.String(description='酒水优惠',default="酒水优惠"),
        "name": hobbys.String(description='饭店名',default="李家馅饼小盘菜"),
        "id": hobbys.String(description='饭店id',default="5733e40a0c1d9b31499888b0"),
        "guide_image": hobbys.String(description='图片',default="ba85cde5af73d26540cec921d69e1eba"),
        "address": hobbys.String(description='地址',default="哈尔滨市南岗区马家街4号"),
        "district_name": hobbys.String(description='行政区名',default="南岗区"),
        "dishes_discount": hobbys.String(description='菜品优惠',default="菜品优惠")
      }

        ]
}

}
#猜你喜欢
@restaurant_user_api.route(settings.app_user_url+'/fm/user/v1/restaurant/hobbys/',methods=['POST'])
@swag_from(hobbys.mylpath(schemaid='hobbys',result=hobbys_json))
def hobbys():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                item = mongo.hobby.find()[0:3]
                list = []
                for i in item:
                    list.append(ObjectId(i['nid']))

                data['list'] = hobby(first={"_id":{"$in":list}},lat1=request.form['lat'],lon1=request.form['lon'],start=0,end=3)
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
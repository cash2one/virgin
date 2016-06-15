#--coding:utf-8--#
import random

import pymongo


from app_merchant import auto
from tools import tools
import time
import sys

from tools.db_app_user import guess

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
                    first["rooms.room_type.id"] = request.form['room_type']
                #特色
                if request.form['tese']!='-1':
                    first["tese.id"] = request.form['tese']
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

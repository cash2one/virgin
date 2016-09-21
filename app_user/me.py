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

me_user_api = Blueprint('me_user_api', __name__, template_folder='templates')





me = swagger("5 我.jpg","账号信息")
me_json = {
    "auto": me.String(description='验证是否成功'),
    "message": me.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": me.Integer(description='',default=0),
    "data": {
        "id": me.String(description='用户id',default="57c3a7d7dcc88e6f2a7bb3ea"),
        "nickname": me.String(description='用户名',default=""),
        "qrcode_img": me.String(description='二维码',default="321e8a465131b29796c162e9147fc1a4"),
        "phone":me.String(description='电话',default="13000000000"),
        "headimage":me.String(description='头像',default="321e8a465131b29796c162e9147fc1a4"),
    }
}
me.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
me.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='5770c069dcc88e5b8591d3bd')

@me_user_api.route('/fm/user/v1/me/me/',methods=['POST'])
@swag_from(me.mylpath(schemaid='me',result=me_json))
def me():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                pass
                data = {}
                webuser_id = request.form['webuser_id']
                item = mongo.webuser.find({"_id":ObjectId(webuser_id)})
                for i in item:
                    data['nickname'] = i['nickname']
                    data['id'] = str(i['_id'])
                    data['qrcode_img'] = i['qrcode_img']
                    data['headimage'] = i['headimage']
                    data['phone'] = i['phone']
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
infos_update = swagger("5-1 账号信息.jpg","账号信息修改")
infos_update_json = {
    "auto": infos_update.String(description='验证是否成功'),
    "message": infos_update.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": infos_update.Integer(description='',default=0),
    "data": {
        "status": infos_update.Integer(description='状态1成功',default=1),
        "msg":infos_update.String(description='返回信息',default="修改成功")
    }
}
infos_update.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
infos_update.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57c3a7d7dcc88e6f2a7bb3ea')
infos_update.add_parameter(name='nickname',parametertype='formData',type='string',required= True,description='用户名',default='57c3a7d7dcc88e6f2a7bb3ea')
infos_update.add_parameter(name='headimage',parametertype='formData',type='string',required= True,description='头像',default='111111111')

@me_user_api.route('/fm/user/v1/me/infos_update/',methods=['POST'])
@swag_from(infos_update.mylpath(schemaid='infos_update',result=infos_update_json))
def infos_update():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                webuser_id = request.form['webuser_id']
                nickname = request.form['nickname']
                headimage = request.form['headimage']
                mongo.webuser.update_one({"_id":ObjectId(webuser_id)},{"$set":{"nickname":nickname, "headimage":headimage}})
                json = {
                        "status": 1,
                        "msg":"修改成功"
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
my_message = swagger("5-2 我的消息.jpg","消息列表")
my_message_json = {
    "auto": my_message.String(description='验证是否成功'),
    "message": my_message.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": my_message.Integer(description='',default=0),
    "data": {
        "list": [
          {
            "status": my_message.Integer(description='状态0未读1已读',default=0),
            "information": my_message.String(description='内容',default="内容"),
            "goto": my_message.String(description='跳转',default="1"),
            "title": my_message.String(description='标题',default="标题"),
            "id": my_message.String(description='消息id',default="5785e120dcc88e5732fdc6e6"),
            "add_time": my_message.String(description='发送时间',default="2016年07月13日 14:35:12"),
          }
        ]
  }
}
my_message.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
my_message.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396fd67c1f31a9cce960f8')
my_message.add_parameter(name='type',parametertype='formData',type='string',required= True,description='1订单信息2优惠信息',default='1')
my_message.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')

@me_user_api.route('/fm/user/v1/me/my_message/', methods=['POST'])
@swag_from(my_message.mylpath(schemaid='my_message',result=my_message_json))
def my_message():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                pageindex = request.form["pageindex"]
                pagenum = 20
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                item = mongo.message.find({"$or":[{"infoto."+str(request.form["webuser_id"]) : 1},{"infoto."+str(request.form["webuser_id"]) : 0}],"type":int(request.form['type'])}).sort("add_time", pymongo.DESCENDING)[star:end]

                data = {}
                list = []
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'infos':
                            json['title'] = i['infos']['infotitle']
                            json['information'] = i['infos']['information']
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M:%S')
                        elif key == 'infoto':
                            json['status'] = i['infoto'][str(request.form["webuser_id"])]
                        elif key == 'goto':
                            json['goto'] = i[key]
                    list.append(json)
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
messageinfo = swagger("5-2 我的消息.jpg","消息详细")
messageinfo_json = {
    "auto": messageinfo.String(description='验证是否成功'),
    "message": messageinfo.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": messageinfo.Integer(description='',default=0),
    "data": {
            "information": messageinfo.String(description='内容',default="内容"),
            "title": messageinfo.String(description='标题',default="标题"),
            "add_time": messageinfo.String(description='发送时间',default="2016年07月13日 14:35:12"),
    }
}
messageinfo.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
messageinfo.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396fd67c1f31a9cce960f8')
messageinfo.add_parameter(name='message_id',parametertype='formData',type='string',required= True,description='消息id',default='5785e120dcc88e5732fdc6e6')

@me_user_api.route('/fm/user/v1/me/messageinfo/', methods=['POST'])
@swag_from(messageinfo.mylpath(schemaid='messageinfo',result=messageinfo_json))
def messageinfo():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.message.find({'_id':ObjectId(request.form['message_id'])})
                json = {}
                for i in item:
                    for key in i.keys():
                        if key == 'infos':
                            json['title'] = i['infos']['infotitle']
                            json['information'] = i['infos']['information']
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M:%S')
                        else:
                            pass
                mongo.message.update({"_id":ObjectId(request.form["message_id"])},{"$set":{"infoto."+request.form['webuser_id']:1}})
                result=tool.return_json(0,"success",True,json)
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
concern_restaurant = swagger("5-3 我的关注.jpg","我的关注列表")
concern_restaurant_json = {
    "auto": concern_restaurant.String(description='验证是否成功'),
    "message": concern_restaurant.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": concern_restaurant.Integer(description='',default=0),
    "data": {
        "list": [
              {
                "name": concern_restaurant.String(description='饭店名',default="顺兴狗肉"),
                "business_dist": concern_restaurant.String(description='商圈名',default="顾乡"),
                "dishes_type": concern_restaurant.String(description='菜系',default="炒菜"),
                "hui": concern_restaurant.String(description='0没有1有惠标签',default="1"),
                "guide_image": concern_restaurant.String(description='饭店头图',default="18d19b3056c5ce33fcf1edc6ffba701c"),
                "district_name": concern_restaurant.String(description='行政区名',default="道里区"),
                "id": concern_restaurant.String(description='饭店id',default="573413c80c1d9b314998895c"),
              }
        ]
    }
}
concern_restaurant.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
concern_restaurant.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
concern_restaurant.add_parameter(name='business_dist_id',parametertype='formData',type='string',required= True,description='商圈id',default='-1')
concern_restaurant.add_parameter(name='district_id',parametertype='formData',type='string',required= True,description='行政区id',default='-1')
concern_restaurant.add_parameter(name='dishes_type',parametertype='formData',type='string',required= True,description='菜系',default='-1')
concern_restaurant.add_parameter(name='discount',parametertype='formData',type='string',required= True,description='优惠',default='-1')
concern_restaurant.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')


#我的关注列表
@me_user_api.route('/fm/user/v1/coupons/concern_restaurant/',methods=['POST'])
@swag_from(concern_restaurant.mylpath(schemaid='concern_restaurant',result=concern_restaurant_json))
def concern_restaurant():
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
                else:
                    if request.form['district_id'] !='-1':
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
                webuser_id_list = []
                item = mongo.concern.find({"webuser_id":ObjectId(request.form['webuser_id'])})
                for i in item:
                    webuser_id_list.append(ObjectId(str(i['restaurant_id'])))
                first['_id'] = {"$in":webuser_id_list}
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
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
mycoupons = swagger("5-5 我的优惠.jpg","我的优惠列表")
mycoupons_json = {
    "auto": mycoupons.String(description='验证是否成功'),
    "message": mycoupons.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": mycoupons.Integer(description='',default=0),
    "data": {
        "list": [
              {
                  "r_name":  mycoupons.String(description='饭店名',default="饭店名"),
                  "content":  mycoupons.String(description='优惠内容',default="优惠内容"),
                  "phone":  mycoupons.String(description='电话',default="电话"),
                  "expiry_date":  mycoupons.String(description='有效期',default="有效期"),
                  "role":  mycoupons.String(description='使用规则',default="使用规则"),
                  "address":  mycoupons.String(description='饭店地址',default="饭店地址")
              }
        ]
    }
}
mycoupons.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
mycoupons.add_parameter(name='webuser_id',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
mycoupons.add_parameter(name='status',parametertype='formData',type='string',required= True,description='1可使用2已使用3已过期',default='1')


#我的优惠列表
@me_user_api.route('/fm/user/v1/coupons/mycoupons/',methods=['POST'])
@swag_from(mycoupons.mylpath(schemaid='mycoupons',result=mycoupons_json))
def mycoupons():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                item = mongo.mycoupons.find({"webuser_id":ObjectId(request.form["webuser_id"])})
                data = {}
                list = []
                status = request.form['status']
                for i in item:
                    json = {
                        "r_name" : i['r_name'],
                        "address" : i['address'],
                        "phone" : i['phone'],
                        "content" : i['content'],
                        "expiry_date" : i['expiry_date'],
                        "role" : i['role'],
                    }
                    if i['status'] == status and i['indate_end']>datetime.datetime.now():
                        print 'in'
                        list.append(json)
                    elif i['status'] == status:
                        list.append(json)
                    else:
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
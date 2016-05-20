#--coding:utf-8--#
import time

import datetime

from app_merchant import auto
from tools import tools
import sys
from flask import Blueprint,abort,request
from connect import conn
from bson import json_util, ObjectId
import tools.tools as tool
reload(sys)
sys.setdefaultencoding('utf8')

table = {
        'restaurant_id': 'obj',
        '_id': 'obj',
        'webuser_id':'obj',
        'nickname':'str',
        'birthday':'str',
        'phone':'str',
        'addtime':'',
        'status':'int',
        'headimage':'str'
      }
mongo=conn.mongo_conn()

members_api = Blueprint('members_api', __name__, template_folder='templates')
#2.0.jpg店粉儿查询|restaurant_id：饭店id |pageindex:页数 |user_tpye:用户类型线下0线上1|
@members_api.route('/fm/merchant/v1/members/allmembers/', methods=['POST'])
def allmembers():
    if request.method=='POST':
        try:
            pdict = {
                'restaurant_id':request.form["restaurant_id"]
            }
            pageindex = request.form["pageindex"]
            pagenum = 10
            star = (int(pageindex)-1)*pagenum
            end = (pagenum*int(pageindex))
            if int(request.form['user_tpye'])==0:
                item = mongo.members.find(tools.orderformate(pdict, table))[star:end]
                data=[]
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                        elif key == 'addtime':
                            json['addtime'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        else:
                            json[key] = i[key]
                    data.append(json)
                data.append({'user_type':0})
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",jwtmsg,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                idlist = []
                concern = mongo.concern.find(tools.orderformate(pdict, table))
                for i in concern:
                    for j in i.keys():
                        if j == 'webuser_id':
                            idlist.append(ObjectId(i[j]))
                item = mongo.webuser.find({'_id': {'$in': idlist}})[star:end]
                data=[]
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'automembers_id':
                            json['automembers_id'] = str(i[key])
                        elif key == 'addtime':
                            json['addtime'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        elif key == 'birthday':
                            json['birthday'] = i[key]
                        elif key == 'gender':
                            json['gender'] = int(i[key])
                        else:
                            json[key] = i[key]
                    data.append(json)
                data.append({'user_type':1})
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",jwtmsg,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#2.1.jpg店粉儿详情查询|restaurant_id:饭店id |_id webuser_id:用户id | user_tpye:用户类型线下0线上1|
@members_api.route('/fm/merchant/v1/members/membersinfo/', methods=['POST'])
def membersinfo():
    if request.method=='POST':
        try:
            pdict = {
                '_id':request.form['id']
            }
            odict = {
                'restaurant_id':request.form["restaurant_id"],
                'webuser_id':request.form['id']
            }
            if int(request.form['user_tpye'])==0:
                item = mongo.members.find_one(tools.orderformate(pdict, table))
                data=[]
                json = {}
                for key in item.keys():
                    if key == '_id':
                        json['id'] = str(item[key])
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(item[key])
                    elif key == 'addtime':
                        json['addtime'] = item[key].strftime('%Y年%m月%d日 %H:%M')
                    elif key == 'birthday':
                        json['birthday'] = item[key]
                    else:
                        json[key] = item[key]
                data.append(json)
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",jwtmsg,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            else:
                item = mongo.webuser.find_one(tools.orderformate(pdict, table))
                totals = mongo.order.find(tools.orderformate(odict, table),{'preset_time':1,'total':1})
                total = {}
                for i in totals:
                    for t in i.keys():
                        if t == '_id':
                            total['id'] = str(i[t])
                        elif t == 'preset_time':
                            total['preset_time'] = str(i[t])
                        else:
                            total[t] = i[t]
                data=[]
                json = {}
                for key in item.keys():
                    if key == '_id':
                        json['id'] = str(item[key])
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(item[key])
                    elif key == 'addtime':
                        json['addtime'] = item[key].strftime('%Y年%m月%d日 %H:%M')
                    elif key == 'birthday':
                        json['birthday'] = item[key]
                    else:
                        json[key] = item[key]
                data.append(json)
                data.append(total)
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",jwtmsg,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#2.0店粉添加
@members_api.route('/fm/merchant/v1/members/insertmembers/', methods=['POST'])
def insertmembers():
    if request.method=='POST':
        try:
            pdict = {
                'nickname':request.form["nickname"],
                'birthday':request.form["birthday"],
                'phone':request.form["phone"],
                'addtime':datetime.datetime.now(),
                'status':request.form["status"],
                'restaurant_id':request.form["restaurant_id"],
                'headimage':request.form["headimage"]
            }
            mongo.members.insert(tools.formatp(pdict, table))
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
#2.0店粉修改id:用户id
@members_api.route('/fm/merchant/v1/members/updatemembers/', methods=['POST'])
def updatemembers():
    if request.method=='POST':
        try:
            pdict = {
                'nickname':request.form["nickname"],
                'birthday':request.form["birthday"],
                'phone':request.form["phone"],
                'status':request.form["status"],
                'restaurant_id':request.form["restaurant_id"],
                'headimage':request.form["headimage"]
            }
            mongo.members.update_one({'_id':ObjectId(request.form['id'])},{"$set":tools.orderformate(pdict, table)})
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

#2.0店粉删除 id:用户id
@members_api.route('/fm/merchant/v1/members/deletemembers/', methods=['POST'])
def deletemembers():
    if request.method=='POST':
        try:
            idlist = request.form['idlist'].split('_')
            midlist = []
            for mid in idlist:
                midlist.append(ObjectId(mid))
            mongo.members.update({"_id":{'$in': midlist}},{"$set":{"status":1}},multi=True)
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
#2.0.jpg店粉儿模糊查询！模糊查询！模糊查询！！！|restaurant_id：饭店id |pageindex:页数 |nickname:用户名|
@members_api.route('/fm/merchant/v1/members/membersbyname/', methods=['POST'])
def membersbyname():
    if request.method=='POST':
        try:
            name = request.form['nickname']
            pageindex = request.form["pageindex"]
            pagenum = 10
            star = (int(pageindex)-1)*pagenum
            end = (pagenum*int(pageindex))
            listall = []
            members = mongo.members.find({"restaurant_id" : ObjectId(request.form["restaurant_id"]),"nickname":{'$regex':name}})
            for i in members:
                dictmembers = {}
                for j in i.keys():
                    if j == '_id':
                        dictmembers['id'] = str(i[j])
                    elif j == 'nickname':
                        dictmembers['nickname'] = i[j]
                    elif j == 'headimage':
                        dictmembers['headimage'] = i[j]
                    dictmembers['user_type'] = 0
                if dictmembers:
                    listall.append(dictmembers)
            idlist = []
            concern = mongo.concern.find({"restaurant_id" : ObjectId(request.form["restaurant_id"])})
            for i in concern:
                for j in i.keys():
                    if j == 'webuser_id':
                        idlist.append(ObjectId(i[j]))
            webusers = mongo.webuser.find({'_id': {'$in': idlist},"nickname":{'$regex':name}})
            for i in webusers:
                dictwebusers = {}
                for j in i.keys():
                    if j == '_id':
                        dictwebusers['id'] = str(i[j])
                    elif j == 'nickname':
                        dictwebusers['nickname'] = i[j]
                    elif j == 'headimage':
                        dictwebusers['headimage'] = i[j]
                    dictwebusers['user_type'] = 1
                if dictwebusers:
                    listall.append(dictwebusers)
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,listall[star:end])
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#--coding:utf-8--#
import time
#3d7fcc68a276303e08563437fd5a87e9
import datetime

import pymongo

from app_merchant import auto
from tools import tools
import sys
from flask import Blueprint,abort,request
from connect import conn
from bson import json_util, ObjectId
import tools.tools as tool
reload(sys)
sys. setdefaultencoding('utf8')

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
        if auto.decodejwt(request.form['jwtstr']):
            try:
                pdict = {
                    'restaurant_id':request.form["restaurant_id"]
                }
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                if int(request.form['user_tpye'])==0:
                    pdict["status"] = 0
                    item = mongo.members.find(tools.orderformate(pdict, table))[star:end]
                    count = mongo.members.find(tools.orderformate(pdict, table)).count()
                    data={}
                    list = []
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
                            json['user_type'] = 0
                        list.append(json)
                    data['list'] = list
                    data['count'] = count
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
                    count = mongo.webuser.find({'_id': {'$in': idlist}}).count()
                    data = {}
                    list = []
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
                            json['user_type'] = 1
                        list.append(json)
                    data['list'] = list
                    data['count'] = count
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
#2.1.jpg店粉儿详情查询|restaurant_id:饭店id |_id webuser_id:用户id | user_tpye:用户类型线下0线上1|
@members_api.route('/fm/merchant/v1/members/membersinfo/', methods=['POST'])
def membersinfo():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    '_id':request.form['id']
                }
                odict = {
                    'restaurant_id':request.form["restaurant_id"],
                    'webuser_id':request.form['id']
                }
                if int(request.form['user_tpye'])==0:
                    item = mongo.members.find_one({'_id':ObjectId(request.form['id'])})
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
                    jwtmsg = auto.decodejwt(request.form["jwtstr"])
                    result=tool.return_json(0,"success",jwtmsg,json)
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    item = mongo.webuser.find_one(tools.orderformate(pdict, table))
                    totals = mongo.order.find(tools.orderformate(odict, table),{'preset_time':1,'total':1}).sort('add_time', pymongo.DESCENDING)[0:2]
                    comment = mongo.comment.find({"restaurant_id":ObjectId(request.form["restaurant_id"]), "user_id":ObjectId(request.form['id'])},{"post_date":1, "user_info.user_name":1,"comment_text":1}).sort('post_date', pymongo.DESCENDING)[0:2]
                    commentlist = []
                    for c in comment:
                        commentdict = {}
                        for d in c.keys():
                            if d == 'post_date':
                                commentdict['post_date'] = c[d].strftime('%Y年%m月%d日 %H:%M')
                            elif d == 'comment_text':
                                commentdict['comment_text'] = c[d]
                            elif d == 'user_info':
                                commentdict['user_name'] = c['user_info']['user_name']
                        commentlist.append(commentdict)
                    totallist = []
                    for i in totals:
                        total = {}
                        for t in i.keys():
                            if t == '_id':
                                total['id'] = str(i[t])
                            elif t == 'preset_time':
                                total['preset_time'] = str(i[t])
                            else:
                                total[t] = i[t]
                        totallist.append(total)
                    data = {}
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
                    data['info'] = json
                    data['total'] = totallist
                    data['comment'] = commentlist
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
#2.0店粉添加
@members_api.route('/fm/merchant/v1/members/insertmembers/', methods=['POST'])
def insertmembers():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    'nickname':request.form["nickname"],
                    'birthday':request.form["birthday"],
                    'phone':request.form["phone"],
                    'addtime':datetime.datetime.now(),
                    'status':'0',
                    'restaurant_id':request.form["restaurant_id"]
                }
                mongo.members.insert(tools.formatp(pdict, table))
                json = {
                        "status": 1,
                        "msg":""
                }
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
#2.0店粉修改id:用户id
@members_api.route('/fm/merchant/v1/members/updatemembers/', methods=['POST'])
def updatemembers():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    'nickname':request.form["nickname"],
                    'birthday':request.form["birthday"],
                    'phone':request.form["phone"],
                    'restaurant_id':request.form["restaurant_id"]
                }
                mongo.members.update_one({'_id':ObjectId(request.form['id'])},{"$set":tools.orderformate(pdict, table)})
                json = {
                        "status": 1,
                        "msg":""
                }
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

#2.0店粉删除 id:用户id
@members_api.route('/fm/merchant/v1/members/deletemembers/', methods=['POST'])
def deletemembers():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                idlist = request.form['idlist'].split('_')
                midlist = []
                for mid in idlist:
                    if mid != '' and mid != None:
                        midlist.append(ObjectId(mid))
                mongo.members.update({"_id":{'$in': midlist}},{"$set":{"status":1}},multi=True)
                json = {
                        "status": 1,
                        "msg":""
                }
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
#2.0.jpg店粉儿模糊查询！模糊查询！模糊查询！！！|restaurant_id：饭店id |pageindex:页数 |nickname:用户名|
@members_api.route('/fm/merchant/v1/members/membersbyname/', methods=['POST'])
def membersbyname():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                name = request.form['nickname']
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                listall = []
                members = mongo.members.find({"restaurant_id" : ObjectId(request.form["restaurant_id"]),"nickname":{'$regex':name}, "status":0})
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
                data = {}
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
                data['list'] = listall[star:end]
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
def sendmes(mfrom='', mto='', title='', info=''):
    try:
        #以下是获取消息来源名
        infofromname = ''
        item = mongo.restaurant.find({"_id":ObjectId(mfrom)})
        for i in item:
            infofromname = i['name']
        #获取消息来源名结束
        #本地消息表接收方id
        infoto = {}
        if mto!='':
            idlist = mto.split('_')
            for mid in idlist:
                if mid != '' and mid != None:
                    infoto[mid] = 0
        insertjson = {
                "infofrom" : ObjectId(mfrom),
                "infoto" : infoto,
                "infos" : {
                    "infotitle" : title,
                    "information" : info,
                    "infofromname" : infofromname
                },
                "type" : 0,
                "add_time" : datetime.datetime.now(),
                "goto":"",
                "is_push":False,
                "channel":"",
                "androidmsg" : "",
                "iosmsg": ""
        }

        mongo.message.insert(insertjson)
        return True

    except:
        return False
#店粉 - 发送消息
@members_api.route('/fm/merchant/v1/members/sendmess/', methods=['POST'])
def sendmess():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:

                if sendmes(mfrom=request.form['restaurant_id'], mto=request.form['webuserids'], title=request.form['title'], info=request.form['info']):
                    json = {
                            "status": 1,
                            "msg":""
                    }
                    result=tool.return_json(0,"success",True,json)
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    result=tool.return_json(0,"field",False,None)
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
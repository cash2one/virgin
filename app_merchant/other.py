#coding=utf-8
from flasgger import swag_from
import connect

__author__ = 'hcy'
from flask import Blueprint,render_template,request,abort
from connect import conn,settings
import pymongo
import tools.tools as tool
from bson import  json_util,ObjectId
import auto
import os
import datetime
from tools.swagger import swagger


from flask import request, Response
import sys
reload(sys)
sys.setdefaultencoding('utf8')
other_api=Blueprint("other_api",__name__,template_folder='templates')
mongo=conn.mongo_conn()

@other_api.route('/fm/merchant/v1/appversion/', methods=['POST'])
def appversion():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
    jwtmsg = auto.decodejwt(jwtstr)
    json={}
    if jwtmsg:
        item=mongo.android_version.find({"appid":1}).sort("addtime",pymongo.DESCENDING)[0]
        json = {
                "url": item["url"],
                "version": item["version"],
                "describe": item["describe"]
        }
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

#安卓版本更新用户版
appversionvuser= swagger("其它","安卓版本更新用户版")
appversionvuser.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
appversionvuser_json = {
  "message": appversionvuser.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "data":{
    "describe":appversionvuser.String(description='更新内容描述',default="39"),
    "url": appversionvuser.String(description='app下载地址',default="http://125.211.222.237/apk/zoyo.apk"),
    "version": appversionvuser.String(description='版本号',default="0.0.1"),
  },
  "code":appversionvuser.Integer(description='',default=0),
}
@other_api.route('/fm/merchant/v1/appversionvuser/', methods=['POST'])
@swag_from(appversionvuser.mylpath(schemaid='appversionvuser',result=appversionvuser_json))
def appversionvuser():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
    jwtmsg = auto.decodejwt(jwtstr)
    json={}
    if jwtmsg:
        item=mongo.android_version.find({"appid":2}).sort("addtime",pymongo.DESCENDING)[0]
        json = {
                "url": item["url"],
                "version": item["version"],
                "describe": item["describe"]
        }
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)


@other_api.route('/fm/merchant/v1/setversion/',methods=['POST'])
def addversion():
    if request.method=="POST":
        addversion=request.form["version"]
        describe=request.form["describe"]
        f = request.files['file']
    if file:
        print  1
        apkname = "meishiditu.apk"
        json={
            "url" : settings.getapk+ apkname,
            "addtime" : datetime.datetime.now(),
            "version" : addversion,
            "describe" : describe
        }

        count = mongo.android_version.count({"version":addversion})
        upload = "/www/site/apk/"+apkname
        f.save(upload)
        if count<=0:
            item = mongo.android_version.insert(json)
        else:
            # item = mongo.android_version.find_one({"version":addversion})
            # json["addtime"]= item["addtime"]
            mongo.android_version.update({"version":addversion},{"url":json["url"],"version":json["version"],"describe":json["describe"]})
        result=tool.return_json(0,"设置成功",True,json)
    else:
        result=tool.return_json(-1,"您没有上传apk文件！",True,"")
    return json_util.dumps(result,ensure_ascii=False,indent=2)

# version <input type="text" name="version">
#     describe <input type="text" name="describe">
#     上传apk<input name="topImage" id="topImage" type="file" />

#上传图片的接口   参数：topImage
@other_api.route('/fm/merchant/v1/uploadimg/', methods=['POST'])
def up():
     if request.method=='POST':
        # if auto.decodejwt(request.form['jwtstr']):
        #     try:
                file = request.files['topImage']
                fname, fext = os.path.splitext(file.filename)
                if file:
                    filename = '%s%s' % (tool.gen_rnd_filename(), fext)
                    # osstr = os.path.dirname(__file__).replace("\\PycharmProjects\\virgin\\app_merchant","/PycharmProjects/virgin")  +'/static2/upload/'+filename
                    osstr = settings.update_img+filename
                    print osstr
                    file.save(osstr)
                    uu = tool.pimg(osstr)
                    u1 = settings.getimageIP + str(uu)
                    os.remove(osstr)
                    print u1
                # jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",True,str(uu))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",False,None)
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        # else:
        #     result=tool.return_json(0,"field",False,None)
        #     return json_util.dumps(result,ensure_ascii=False,indent=2)


@other_api.route('/fm/merchant/v1/addfeedback/',methods=['POST'])
def addfeedback():
    # try:
        if request.method == 'POST':
            content=request.form['content']
            # email=request.form['email']
            webuserid=request.form['userid']
            jwtstr = request.form["jwtstr"]
        jwtmsg = auto.decodejwt(jwtstr)
        item={
              "webuserid" : ObjectId(webuserid),
              "email":"",
              "contents" : content,
              "addtime" :datetime.datetime.now(),
              "isread" : 2,
              "reContents" : "",
              "userid" : ObjectId("000000000000000000000000"),
              "source":1
        }
        feedback=mongo.addfeedback.insert_one(item)
        result=tool.return_json(0,"success",jwtmsg,{"status":True})
        return json_util.dumps(result,ensure_ascii=False,indent=2)

#安卓版本更新用户版
addfeedbackvuser= swagger("其它","用户版意见反馈")
addfeedbackvuser.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
addfeedbackvuser.add_parameter(name='userid',parametertype='formData',type='string',required= True,description='用户id',default='57396ec17c1f31a9cce960f4')
addfeedbackvuser.add_parameter(name='content',parametertype='formData',type='string',required= True,description='反馈内容',default='美食地图我喜欢')
addfeedbackvuser_json ={
  "auto": addfeedbackvuser.Boolean(description='',default="true"),
  "message": addfeedbackvuser.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "code": addfeedbackvuser.Integer(description='',default=0),
  "data": {
    "status": addfeedbackvuser.Boolean(description='true-添加成功/flase-添加失败',default="true"),
  }
}
@other_api.route('/fm/merchant/v1/addfeedbackvuser/',methods=['POST'])
@swag_from(addfeedbackvuser.mylpath(schemaid='addfeedbackvuser',result=addfeedbackvuser_json))
def addfeedbackvuser():
    # try:
        if request.method == 'POST':
            content=request.form['content']
            # email=request.form['email']
            webuserid=request.form['userid']
            jwtstr = request.form["jwtstr"]
        jwtmsg = auto.decodejwt(jwtstr)
        item={
              "webuserid" : ObjectId(webuserid),
              "email":"",
              "contents" : content,
              "addtime" :datetime.datetime.now(),
              "isread" : 2,
              "reContents" : "",
              "userid" : ObjectId("000000000000000000000000"),
              "source":2
        }
        feedback=mongo.addfeedback.insert_one(item)
        result=tool.return_json(0,"success",jwtmsg,{"status":True})
        return json_util.dumps(result,ensure_ascii=False,indent=2)
        #
        # feedback=mongo.zoyo_feedback.insert_one(item)
        # return render_template('other/feedback.html',statecode=1)
    # except Exception,e:
    #     return render_template('other/feedback.html',statecode=0)

#newcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":0}).count()
#首页新订单数和新推送消息数
@other_api.route('/fm/merchant/v1/counts/',methods=['POST'])
def counts():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                newordercount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":0}).count()
                newmessagecount = mongo.message.find({"infoto."+str(request.form["restaurant_id"]) : 0}).count()
                data = {}
                data['neworder'] = str(newordercount)
                data['newmessage'] = str(newmessagecount)
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
#获取用户表二维码
@other_api.route('/fm/merchant/v1/getqrcode/',methods=['POST'])
def getqrcode():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                item = mongo.webuser.find({"_id":ObjectId(request.form['webuser_id'])})
                qrcode_img = ''
                for i in item:
                    qrcode_img = i['qrcode_img']
                result=tool.return_json(0,"SUCCESS",True,qrcode_img)
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

#扫二维码
@other_api.route('/fm/merchant/v1/webuserqrcode/',methods=['POST'])
def webuserqrcode():
    if auto.decodejwt(request.form['jwtstr']):
        json={
            "url":"/fm/merchant/v1/me/webuserqrcodehtml/",
            "restaurant_id": request.form['restaurant_id'],
            "webuser_id" : request.form['webuser_id']
        }


        result=tool.return_json(0,"success",True,json)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        result=tool.return_json(0,"field",False,None)
        return json_util.dumps(result,ensure_ascii=False,indent=2)


@other_api.route('/fm/merchant/v1/me/webuserqrcodehtml/',methods=["GET"])
def abouthtml():
    return render_template("/test/webuserqrcode.html")

#分享
@other_api.route('/fm/merchant/v1/share/',methods=['POST'])
def share():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.fenxiang.find()
                json = {}
                for i in item:
                    json['title'] = i['Title']
                    json['content'] = i['Content']
                    json['img'] = i['img']
                    json['url'] = i['url']
                result=tool.return_json(0,"SUCCESS",True,json)
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
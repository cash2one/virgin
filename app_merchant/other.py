#coding=utf-8
import connect

__author__ = 'hcy'
from flask import Blueprint,render_template,request,abort
from connect import conn
import pymongo
import tools.tools as tool
from bson import  json_util,ObjectId
import auto
import os
import datetime


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
        item=mongo.android_version.find().sort("addtime",pymongo.DESCENDING)[0]
        json = {
                "url": item["url"],
                "version": item["version"],
                "describe": item["describe"]
        }
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

#上传图片的接口   参数：topImage
@other_api.route('/fm/merchant/v1/uploadimg/', methods=['POST'])
def up():
     if request.method=='POST':
        # if auto.decodejwt(request.form['jwtstr']):
            try:
                file = request.files['topImage']
                fname, fext = os.path.splitext(file.filename)
                if file:
                    filename = '%s%s' % ('test', fext)
                    osstr = os.path.dirname(__file__).replace("\\PycharmProjects\\virgin\\app_merchant","/PycharmProjects/virgin")  +'/static/upload/'+filename
                    print osstr
                    file.save(osstr)
                    uu = tool.pimg(osstr)
                    u1 = connect.conn.imageIP + uu
                    os.remove(osstr)
                    print u1
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result=tool.return_json(0,"success",jwtmsg,uu)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
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
              "userid" : ObjectId("000000000000000000000000")
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
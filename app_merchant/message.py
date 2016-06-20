#--coding:utf-8--#
import pymongo


from app_merchant import auto
from tools import tools
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime
import requests
mongo=conn.mongo_conn()
mongouser=conn.mongo_conn_user()

message_api = Blueprint('message_api', __name__, template_folder='templates')
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|type-0系统发 1商家发 2用户发
def tuisong(mfrom='', mto='57396ec17c1f31a9cce960f4_57329b1f0c1d9b2f4c85f8e3', title='', info='',type='0',appname='foodmap_user',msgtype='message',ispost=True):

    try:
        #以下是获取消息来源名
        infofromname = ''
        if type == '0':
            item = mongo.webuser.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['nickname']
        elif type == '1':
            item = mongo.restaurant.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['name']
        elif type == '2':
            item = mongo.webuser.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['nickname']
        else:
            pass
            infofromname = '未知'

        infoto = {}
        idlist = mto.split('_')
        identandroid = ''
        identios = ''
        for mid in idlist:
            if mid != '' and mid != None:
                infoto[mid] = 0
                #mid是接收方id 下面webuser是查询用户中心id
                webuser = mongo.webuser.find({"_id":ObjectId(mid)})
                for w in webuser:
                    #查询用户中心表usercenter得到设备类型和设备号
                    usercenter = mongouser.user_web.find({"_id":ObjectId(w['automembers_id'])})
                    for u in usercenter:
                        #0是安卓1是IOS
                        if u['lastlogin']['type'] == '0':
                            #拼接TargetValue参数
                            identandroid = identandroid+u['lastlogin']['ident']+","
                        else:
                            identios = identios+u['lastlogin']['ident']+","
        androidmsg = {}
        iosmsg = {}
        if msgtype == 'message':
            if identandroid!='' and ispost:
                androidmsg = {"appname": appname, "type": msgtype, "Message": info, "Target": "device", "TargetValue": identandroid}
                req = requests.post('http://125.211.222.237:11035/push.android',data=androidmsg)
            if identios!='' and ispost:
                iosmsg = {"appname": appname, "type": msgtype, "Message": info, "Summary": title, "Target": "device", "TargetValue": identios}
                req = requests.post('http://125.211.222.237:11035/push.ios',data=iosmsg)
        else:
            if identandroid!='' and ispost:
                androidmsg = {"appname": appname, "type": msgtype, "Title": title, "Summary": info, "Target": "device", "TargetValue": identandroid}
                req = requests.post('http://125.211.222.237:11035/push.android',data=androidmsg)
            if identios!='' and ispost:
                iosmsg = {"appname": appname, "type": msgtype, "Summary": info, "Target": "device", "TargetValue": identios}
                req = requests.post('http://125.211.222.237:11035/push.ios',data=iosmsg)
        # androidmessage = {"appname": appname, "type": msgtype, "Message": info, "Target": "all", "TargetValue": "all"}
        # androidnoticee = {"appname": appname, "type": msgtype, "Title": title, "Summary": info, "Target": "all", "TargetValue": "all"}
        # iosmessage = {"appname": appname, "type": msgtype, "Message": info, "Summary": title, "Target": "all", "TargetValue": "all"}
        # iosnotice = {"appname": appname, "type": msgtype, "Summary": info, "Target": "all", "TargetValue": "all"}
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
                "androidmsg" : androidmsg,
                "iosmsg": iosmsg
        }
        mongo.message.insert(insertjson)
    except:
        return False
    return True
#推送
@message_api.route('/fm/merchant/v1/message/sendmessage/', methods=['POST'])
def sendmessage():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                msg = {"appname": "foodmap_user", "type": "message", "Message": "test Message!", "Target": "all", "TargetValue": "all"}
                req = requests.post('http://125.211.222.237:11035/push.android',data=msg)
                data['requests'] = req.json()
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

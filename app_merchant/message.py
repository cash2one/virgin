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

message_api = Blueprint('message_api', __name__, template_folder='templates')

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

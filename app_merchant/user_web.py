#coding=utf-8
import connect


from flask import Blueprint,render_template,request,abort
from connect import conn,settings
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
mongouser=conn.mongo_conn_user()
@other_api.route('/fm/merchant/v1/user_web/updateident/', methods=['POST'])
def updateident():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                lastlogin = {
                                "ident" : request.form['ident'],
                                "type" : request.form['type'],
                                "time" : datetime.datetime.now()
                            }
                item = mongouser.user_web.update({{"_id":ObjectId(request.form['user_web_id'])},{"$set":{"lastlogin":lastlogin}}})
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"field",False,json)
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

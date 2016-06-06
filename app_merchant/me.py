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

mongo=conn.mongo_conn()

me_api = Blueprint('me_api', __name__, template_folder='templates')

#推送记录查询 条件是时间
@me_api.route('/fm/merchant/v1/me/messages/', methods=['POST'])
def messages():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                start=datetime.datetime(*time.strptime(request.form['start_time'],'%Y-%m-%d')[:6])
                end = datetime.datetime(*time.strptime(request.form['end_time'],'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
                item = mongo.message.find({'infofrom':ObjectId(request.form["restaurant_id"]),'add_time': {'$gte': start, '$lt': end}})

                data = {}
                list = []
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'infos':
                            json['title'] = i['infos']['infotitle']
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日')
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
#推送记录内容查询 条件是id
@me_api.route('/fm/merchant/v1/me/messageinfo/', methods=['POST'])
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
                            json['count'] = len(i['infoto'])
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
#关于我们内容查询
@me_api.route('/fm/merchant/v1/me/aboutus/', methods=['POST'])
def aboutus():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.aboutus.find()
                json = {}
                for i in item:
                    for key in i.keys():
                        json[key] = i[key]
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
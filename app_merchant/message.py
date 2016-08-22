#--coding:utf-8--#
import pymongo


from app_merchant import auto
from tools import tools
import time
import sys

from tools.message_template import mgs_template

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
#接单 推送yh_3
@message_api.route('/fm/merchant/v1/message/sendmessage_yh_3/', methods=['POST'])
def sendmessage_yh_3():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:

                order = mongo.order.find({"_id":ObjectId(request.form['order_id'])})
                name = ''
                roomid = ''
                data = ''
                dishslist = []
                for o in order:
                    name = o['username']
                    roomid = o['room_id']
                    data = o['preset_time'].strftime('%Y年%m月%d日 %H:%M')
                    o['preset_dishs'].extend( o['preset_wine'])
                    for dish in o['preset_dishs']:
                        dishslist.append(dish['name']+':'+str(dish['discount_price'])+'元X'+str(dish['num'])+'份')
                dishs = ',\n'.join(dishslist)
                restaurant = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                redname = ''
                roomname = ''
                address = ''
                phone = ''
                for r in restaurant:
                    redname = r['name']
                    address = r['address']
                    phone = r['phone']
                    for room in r['rooms']:
                        if room['room_id'] ==roomid:
                            roomname = room['room_name']
                print (mgs_template["yh_3"]["text"]%{"name":name,"redname":redname,"data":data,"roomname":roomname,"dishs":dishs,"address":address,"phone":phone})
                item = tool.tuisong(mfrom=request.form['restaurant_id'],
                             mto=request.form['webuserids'],
                             title='美食地图',
                             info=mgs_template["yh_3"]['title'],
                             goto=mgs_template["yh_3"]['goto'],
                             channel=mgs_template["yh_3"]['channel'],
                             type='1',
                             totype='1',
                             appname='foodmap_shop',
                             msgtype='notice',
                             target='device',
                             ext='{"goto":'+mgs_template["yh_3"]['goto']+'}',
                             ispush=True)
                result=tool.return_json(0,"success",True,item)
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
#拒单 推送yh_6
@message_api.route('/fm/merchant/v1/message/sendmessage_yh_6/', methods=['POST'])
def sendmessage_yh_6():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
                print (mgs_template["yh_6"]["text"]%{"data":data})
                item = tool.tuisong(mfrom=request.form['restaurant_id'],
                             mto=request.form['webuserids'],
                             title='美食地图',
                             info=mgs_template["yh_6"]['title'],
                             goto=mgs_template["yh_6"]['goto'],
                             channel=mgs_template["yh_6"]['channel'],
                             type='1',
                             totype='1',
                             appname='foodmap_shop',
                             msgtype='notice',
                             target='device',
                             ext='{"goto":'+mgs_template["yh_6"]['goto']+'}',
                             ispush=True)
                result=tool.return_json(0,"success",True,item)
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




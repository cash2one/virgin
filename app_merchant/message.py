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
#接单 推送11
@message_api.route('/fm/merchant/v1/message/sendmessage_yh_3/', methods=['POST'])
def sendmessage_yh_3():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                item = tool.tuisong(mfrom=request.form['restaurant_id'],
                             mto=request.form['webuserids'],
                             title='您的订座已被安排',
                             info='快去看看吧！',
                             goto='11',
                             channel='接单',
                             type='1',
                             totype='1',
                             appname='foodmap_user',
                             msgtype='notice',
                             target='device',
                             ext='{"goto":"11","id":"'+request.form['order_id']+'"}',
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
#接单推送12
@message_api.route('/fm/merchant/v1/message/sendmessage_yh_31/', methods=['POST'])
def sendmessage_yh_31():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                item = tool.tuisong(mfrom=request.form['restaurant_id'],
                             mto=request.form['webuserids'],
                             title='您的点菜已被安排',
                             info='快去看看吧！',
                             goto='12',
                             channel='接单',
                             type='1',
                             totype='1',
                             appname='foodmap_user',
                             msgtype='notice',
                             target='device',
                             ext='{"goto":"12","id":"'+request.form['order_id']+'"}',
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
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                rest = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                phone = ''
                r_name = ''
                for r in rest:
                    phone = r['phone']
                    r_name = r['name']
                order = mongo.order.find({"_id":ObjectId(request.form['order_id'])})
                addtime = ''
                for o in order:
                    addtime = o['add_time']
                item = tool.tuisong(mfrom=request.form['restaurant_id'],
                             mto=request.form['webuserids'],
                             title=r_name,
                             info='您在'+addtime.strftime('%Y年%m月%d日 %H:%M:%S')+'向'+r_name+
                                  '发出了就餐需求，十分抱歉，该饭店预订已满，无法为您安排就餐，如有疑问请拨打商家电话：'+phone,
                             goto='19',
                             channel='商家拒单',
                             type='1',
                             totype='1',
                             appname='foodmap_user',
                             msgtype='notice',
                             target='device',
                             ext='',
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




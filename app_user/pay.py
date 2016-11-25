#--coding:utf-8--#
import random
import time
import pymongo
import requests
from flasgger import swag_from

from app_merchant import auto
from app_user.groupinvite import GroupInvite
from tools import tools

import sys

from tools.db_app_user import guess, business_dist, district_list, business_dist_byid, getcoupons, getconcern, checkdish, \
    coupons_by, use_coupons, getimg
from tools.message_template import mgs_template
from tools.payclass import PayOrder
from tools.swagger import swagger

reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime
import connect.settings as settings

mongo=conn.mongo_conn()

pay_user_api = Blueprint('pay_user_api', __name__, template_folder='templates')

deal = swagger("支付","订单支付")
deal_json = {
    "auto": deal.String(description='验证是否成功'),
    "message": deal.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": deal.Integer(description='',default=0),
    "data": {
        "id":deal.String(description='SUCCESS/FIELD',default="SUCCESS"),
        "subject":deal.String(description='SUCCESS/FIELD',default="美食地图某某饭店订单名"),
        "total_fee":deal.Integer(description='支付金额(分)',default=10000),
    }
}
deal.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
deal.add_parameter(name='type',parametertype='formData',type='string',required= True,description='订单传order 开团传group',default='order')
deal.add_parameter(name='deal_id',parametertype='formData',type='string',required= True,description='订单或者开团请客id',default='573153c4e0fdb78f29b42826')

@pay_user_api.route(settings.app_user_url+'/fm/user/v1/pay/deal/',methods=['POST'])
@swag_from(deal.mylpath(schemaid='deal',result=deal_json))
def deal():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                data = {}
                pay = PayOrder()
                type = request.form['type']
                if type == 'order':
                    pay.link_order(request.form['deal_id'])
                elif type == 'group':
                    pay.link_group(request.form['deal_id'])
                else:
                    pass

                data['id'] = pay.payorder_id
                data['subject'] = pay.payorder['subject']
                data['total_fee'] = pay.payorder['total_fee']
                result=tool.return_json(0,"success",True,data)
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
payorder = swagger("支付","发起支付")
payorder_json = {
    "auto": payorder.String(description='验证是否成功'),
    "message": payorder.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": payorder.Integer(description='',default=0),
    "data": {
          "status": payorder.String(description='状态',default="new"),
          "PaymentID": payorder.String(description='id',default="1475129175666"),
          "pay_url": payorder.String(description='地址',default="https://"),
          "pay_data": payorder.String(description='数据',default="{}")
    }
}
payorder.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
payorder.add_parameter(name='payOrder_id',parametertype='formData',type='string',required= True,description='支付订单id',default='57ecbd62fb98a416503ce901')
payorder.add_parameter(name='service',parametertype='formData',type='string',required= True,description='支付方式 支付宝alipay 微信wxpay',default='wxpay')

@pay_user_api.route(settings.app_user_url+'/fm/user/v1/pay/payorder/',methods=['POST'])
@swag_from(payorder.mylpath(schemaid='payorder',result=payorder_json))
def payorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                payOrder_id = request.form['payOrder_id']
                pay = PayOrder(payOrder_id)
                service = request.form['service']
                data = pay.req_pay(service)
                result=tool.return_json(0,"success",True,data)
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
update_order = swagger("支付","回调")
update_order_json = {
    "auto": update_order.String(description='验证是否成功'),
    "message": update_order.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": update_order.Integer(description='',default=0),
    "data": {
          "status": update_order.String(description='状态',default="new")
    }
}
update_order.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
update_order.add_parameter(name='payment_id',parametertype='formData',type='string',required= True,description='支付订单id',default='1479883957816')

@pay_user_api.route(settings.app_user_url+'/fm/user/v1/pay/update_order/',methods=['POST'])
@swag_from(update_order.mylpath(schemaid='update_order',result=update_order_json))
def update_order():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                payment_id = request.form['payment_id']
                data = requests.get("http://127.0.0.1:10036/api/v1/payment/"+payment_id).json()
                flag = {"success":"0"}
                if data['status'] =='SUCCESS_PAY':
                    pay_order = mongo.payOrder.find({"orderid":data["OrderID"]})
                    oid = ""
                    reqfrom = ""
                    for p in pay_order:
                        reqfrom = p['reqfrom']
                        oid = p['req_order_id']
                    if reqfrom == 'MSDT_order_app':
                        mongo.order.update({"_id":ObjectId(oid)},{"$set":{"status":3}})
                    else:
                        mongo.order_groupinvite.update({"_id":ObjectId(oid)},{"$set":{"status":"already_used"}})
                    flag = {"success":"1"}
                else:
                    pass
                result=tool.return_json(0,"success",True,flag)
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
if __name__ == '__main__':
    data = requests.get("http://125.211.222.237:11036/api/v1/payment/1479883957816").json()
    print json_util.dumps(data,ensure_ascii=False,indent=2)
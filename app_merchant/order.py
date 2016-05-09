#--coding:utf-8--#
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime
import time


mongo=conn.mongo_conn()

order_api = Blueprint('order_api', __name__, template_folder='templates')

@order_api.route('/fm/merchant/1.0/order/addorder',methods=['POST'])
def addorder():
    if request.method == 'POST':
        username=request.form['username']
        phone=request.form['phone']
        numpeople=request.form['numpeople']
        is_room=request.form['is_room']
        preset_time=request.form['preset_time']
        demand=request.form['demand']
        preset_dishs=request.form['preset_dishs']
        source=request.form['source']
        if request.form['deposit']=="":
            deposit = 0
        else:
            deposit=request.form['deposit']
        type = request.form['type']
        restaurant_id=request.form['restaurant_id']
        room_id=request.form['room_id']
        webuser_id=request.form['webuser_id']
        dis_message=request.form['dis_message']
        preset_dishs=[]
    json = {
        "username": username, #1
        "phone": phone,#1
        "numpeople": int(numpeople),#1
        "is_room": bool(is_room),#1
        "preset_time":  preset_time,#1
        "add_time":datetime.datetime.now(),#1
        "demand": demand,#1
        "status": 0,#1
        "source": int(source),#1
        "restaurant_id": ObjectId(restaurant_id),#1
        "room_id": room_id,
        "webuser_id": ObjectId(webuser_id),#1
        "deposit": float(deposit),
        "dis_message": dis_message,#1
        "type": int(type),#1
        "preset_dishs":preset_dishs#1
    }
    mongo.order.insert_one(json)
    result=tool.return_json(0,"success",json_util.dumps(json))
    return result




@order_api.route('/fm/merchant/1.0/order/onedishsorder/<string:order_id>/<int:order_type>', methods=['GET'])
def onedishsorder(order_id,order_type):
    item = mongo.order.find_one({"_id":ObjectId(order_id)})
    item = json_util.loads(json_util.dumps(item))
    if order_type==0:#��λ����
        json = {
            "demand":item["demand"],
            "roomlist":list(public.getroomslist(str(item["restaurant_id"])))
        }
    else:#��Ʒ����
        amount=0.0
        for i in item["preset_dishs"]:
            if i["discount_price"]=="":
                amount+=i["price"]
            else:
                amount+=float(i["discount_price"])
        json= {
            "demand":item["demand"],
            "dis_message":item["dis_message"],
            "amount":amount,
            "roomlist":public.getroomslist(str(item["_id"]))
        }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)




@order_api.route('/fm/merchant/1.0/order/dispose/<string:order_id>', methods=['GET'])
def onedishsorder(order_id):
    item = mongo.order.find_one({"_id":ObjectId(order_id)})
    item = json_util.loads(json_util.dumps(item))
    json = {
            "username": item["username"],
            "phone": item["phone"],
            "numpeople": int(item["numpeople"]),
            "is_room": bool(item["is_room"]),
            "preset_time":  item["preset_time"],
            "demand": item["demand"],
            "preset_dishs":item["preset_dishs"]
        }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)






@order_api.route('/fm/merchant/1.0/order/accept/<string:order_id>', methods=['PUT'])
def onedishsorder(order_id):
    room_id = request.form["room_id"]
    deposit = request.form["deposit"]  # 订金：之后需要根据指定规则进行修改
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"room_id":room_id,"deposit":deposit,"status":1}})
    json = {
            "order_id": item,
            "status": 1,
            "msg":""
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)




@order_api.route('/fm/merchant/1.0/order/decline/<string:order_id>', methods=['PUT'])
def onedishsorder(order_id):
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"status":2}})
    json = {
            "order_id": item,
            "status": 2,
            "msg":""
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)


@order_api.route('/fm/merchant/1.0/order/notification/<string:order_id>', methods=['PUT'])
def onedishsorder(order_id):
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"status":2}})
    json = {
            "order_id": item,
            "status": 2,
            "msg":""
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

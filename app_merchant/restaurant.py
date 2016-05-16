#--coding:utf-8--#
from tools import tools

from flask import Blueprint,request
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool

table = {'status': 'int',
         'type': 'int',
         'restaurant_id': 'obj',
         '_id': 'obj',
         'menu.dish_type':'str',
      }
dishes_discount = {
    'dishes_discount.discount':'int',
    'dishes_discount.message':'str',
    'dishes_discount.end_time':'str',
    'dishes_discount.start_time':'str',
    'dishes_discount.desc':'str',
}

mongo=conn.mongo_conn()

restaurant_api = Blueprint('restaurant_api', __name__, template_folder='templates')

#1.4菜品优惠查询form:id
@restaurant_api.route('/fm/merchant/1.0/restaurant/restaurant_discount', methods=['POST'])
def restaurant_discount():
    pdict = {
        '_id':request.form["id"],
        'menu.dish_type':request.form['dish_type']
    }
    print pdict
    print tools.orderformate(pdict, table)
    item = mongo.restaurant.find(tools.orderformate(pdict, table))
    print item
    data=[]
    for i in item:
        json = {}
        for key in i.keys():
            if key == '_id':
                json['id'] = i[key]
            else:
                json[key] = i[key]
        print json
        data.append(json)

    result=tool.return_json(0,"success",data)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

@restaurant_api.route('/fm/merchant/1.0/restaurant/updaterestaurant', methods=['POST'])
def updaterestaurant():
    pdict = {
        "dishes_discount.discount":request.form['discount'],
        "dishes_discount.message":request.form['message'],
        "dishes_discount.end_time":request.form['end_time'],
        "dishes_discount.start_time":request.form['start_time'],
        "dishes_discount.desc":request.form['desc']
    }
    objid = {"_id":ObjectId(request.form["id"])}
    first = tools.orderformate(pdict,dishes_discount)
    second = {"$set":first}
    mongo.restaurant.update_one(objid,second)

    dish = {
        request.form['dish_id']: {'discount_price': float(request.form['discount_price'])}
    }
    redish = tool.Foormat(request.form["id"]).re_dish(dish)
    redish.submit2db()
    json = {
            "status": 1,
            "msg":""
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

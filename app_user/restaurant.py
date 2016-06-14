#--coding:utf-8--#
import random

import pymongo


from app_merchant import auto
from tools import tools
import time
import sys

from tools.db_app_user import guess

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

restaurant_user_api = Blueprint('restaurant_user_api', __name__, template_folder='templates')
#饭店列表 条件很多
@restaurant_user_api.route('/fm/user/v1/index/index/',methods=['POST'])
def index():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                data = {}
                first = {"dishes_type.id":"10","dishes_discount.message":{"$ne":""},"rooms.room_type.id":"36","tese.id":"54","pay_type.id":{"$in":["48"]},"_id":{"$in":[ObjectId("57329e300c1d9b2f4c85f8e6")]}}
                if request.form['dishes_type']!='-1':
                    first["pay_type.id"] = int(request.form['dishes_type'])
                if request.form['discount']!='-1':
                    if request.form['discount'] == 'dish':
                        first["dishes_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'wine':
                        first["wine_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'wine':
                        first["restaurant_discount.message"] = {"$ne":""}
                if request.form['room_type']!='-1':
                    pass
                if request.form['tese']!='-1':
                    pass
                if request.form['pay_type']!='-1':
                    pass
                    idlist = request.form['pay_type'].split('_')
                    midlist = []
                    for mid in idlist:
                        if mid != '' and mid != None:
                            midlist.append(ObjectId(mid))
                    first["pay_type.id"] = {"$in":midlist}
                if request.form['recommend']!='-1':
                    pass
                    if request.form['recommend_type']!='-1':
                        item = mongo.shop_recommend.find({"type":1},{"_id":1})
                    else:
                        item = mongo.shop_recommend.find({},{"_id":1})
                    r_idlist = []
                    for i in item:
                        r_idlist.append(i['_id'])
                    first['_id'] = {"$in":r_idlist}
                list = guess(first=first,start=0,end=10000)
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
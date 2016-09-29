#--coding:utf-8--#
import random

import pymongo


from app_merchant import auto
from tools import tools
import time
import sys

from tools.db_app_user import getcoupons, getimg, guess

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

index_api = Blueprint('index_api', __name__, template_folder='templates')
#首页大接口 暂缺开团请客
@index_api.route('/fm/user/v1/index/index/',methods=['POST'])
def index():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                data = {}
                #开团请客 开始
                #暂缺
                #开团请客 结束
                #店粉优惠 随机两个饭店 开始
                count = len(mongo.coupons.distinct('restaurant_id',{'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()},"button":"0"}))
                randomnum = random.randint(0, count-2)
                restaurant_id = mongo.coupons.distinct('restaurant_id',{'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()},"button":"0"})[randomnum:randomnum+2]
                idlist = []
                for i in restaurant_id:
                    idlist.append(i)
                coupons = {}
                couponslist = []
                num = 0
                for i in idlist:
                    coupons['title1'] = getcoupons('1',idlist[num])['content']
                    coupons['id1'] = getcoupons('1',idlist[num])['id']
                    coupons['title2'] = getcoupons('2',idlist[num])['content']
                    coupons['id2'] = getcoupons('2',idlist[num])['id']
                    coupons['title3'] = getcoupons('3',idlist[num])['content']
                    coupons['id3'] = getcoupons('3',idlist[num])['id']
                    coupons['img'] = getimg(idlist[num])
                    num+=1
                    couponslist.append(coupons)
                data['coupons'] = couponslist
                #店粉优惠 随机两个饭店 结束
                #店粉优惠专用图片 开始
                image = mongo.img.find()
                imgjson = {}
                for img in image:
                    imgjson['img'] = img['img']
                    imgjson['title'] = img['title']
                data['img'] = imgjson
                #店粉优惠专用图片 结束
                #今日范儿店 开始
                shop_recommend = mongo.shop_recommend.find({'type':1,'showtime': {'$gte': datetime.datetime.now()-datetime.timedelta(days = 1),'$lt': datetime.datetime.now()}}).sort("addtime", pymongo.DESCENDING)[0:1]
                recommend = {}
                for i in shop_recommend:

                    for key in i.keys():
                        if key == '_id':
                            recommend['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            recommend['restaurant_id'] = str(i[key])
                        elif key == 'restaurant_name':
                            recommend['restaurant_name'] = i[key]
                        elif key == 'content':
                            recommend['content'] = i[key]
                        elif key == 'dishs':
                            recommend['dishs'] = i[key][0:3]
                        else:
                            pass
                data['recommend'] = recommend
                #今日范儿店 结束
                #猜你喜欢 开始
                guesslist = guess(lat1=float(request.form['x']),lon1=float(request.form['y']))
                data['guess'] = guesslist
                #猜你喜欢 结束
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
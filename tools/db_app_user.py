#--coding:utf-8--#
import pymongo
import sys
from math import radians, cos, sin, asin, sqrt

reload(sys)
sys.setdefaultencoding('utf8')
from connect import conn
from bson import ObjectId,json_util
import datetime

mongo=conn.mongo_conn()
#根据类别和饭店id获取一条店粉优惠
def getcoupons(kind, restaurant_id):
    item = mongo.coupons.find({'restaurant_id':ObjectId(restaurant_id),'kind':kind,'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()}}).sort("showtime_start", pymongo.DESCENDING)[0:1]
    json = {}
    json['id'] =  ''
    json['content'] =  ''
    for i in item:
        json['id'] = str(i['_id']) if str(i['_id'])!='' else ''
        json['content'] = i['content'] if i['content']!='' else ''
    return json
#获取首页店粉优惠大图
def getimg(restaurant_id):
    item = mongo.restaurant.find({"_id":ObjectId(restaurant_id)},{'guide_image':1})
    for i in item:
        for key in i.keys():
            if key == 'guide_image':
                img = i[key]
    return img
#根据商圈id获取行政区
def getxingzhengqu(xid):
    item = mongo.district.find({"biz_areas.biz_area_id":int(xid)},{"district_name":1})
    for i in item:
        return i["district_name"]
#经纬度算距离
def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）

    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000
#根据获取的经纬度查询若干条距离最近的饭店信息
def guess(first={},lat1=45.76196769636328,lon1=126.65381534034498,start=0,end=3):
    if lat1!='x':
        item = mongo.restaurant.find(first,{"zuobiao":1})
        rsetaurant_list = []
        for i in item:
            rsetaurant_list.append((int(haversine(lon1, lat1, i['zuobiao'][0]['c1'], i['zuobiao'][0]['c2'])), str(i['_id'])))
        list=[]
        for l in sorted(rsetaurant_list)[start:end]:
            restaurant = mongo.restaurant.find({'_id':ObjectId(l[1])})

            for rest in restaurant:
                json = {}
                for key in rest.keys():
                    if key == '_id':
                        json['id'] = str(rest[key])
                        json['kind1'] = getcoupons('1',rest[key])['content']
                        json['kind2'] = getcoupons('2',rest[key])['content']
                        json['kind3'] = getcoupons('3',rest[key])['content']
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(rest[key])
                    elif key == 'name':
                        json['name'] = rest[key]
                    elif key == 'guanzhu_discount':
                        json['guanzhu_discount'] = rest[key]['message']
                    elif key == 'dishes_discount':
                        json['dishes_discount'] = rest[key]['message']
                    elif key == 'business_dist':
                        json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                        json['business_name'] = rest[key][0]['name']
                    elif key == 'guide_image':
                        json['guide_image'] = rest[key]
                    elif key == 'address':
                        json['address'] = rest[key]
                    elif key == 'wine_discount':
                        json['wine_discount'] = rest[key]['message']
                    else:
                        json['distance'] = l[0]
                list.append(json)
    else:
        restaurant = mongo.restaurant.find(first).sort("addtime", pymongo.DESCENDING)[start:end]
        list = []
        for rest in restaurant:
            json = {}
            for key in rest.keys():
                if key == '_id':
                    json['id'] = str(rest[key])
                    json['kind1'] = getcoupons('1',rest[key])['content']
                    json['kind2'] = getcoupons('2',rest[key])['content']
                    json['kind3'] = getcoupons('3',rest[key])['content']
                elif key == 'restaurant_id':
                    json['restaurant_id'] = str(rest[key])
                elif key == 'name':
                    json['name'] = rest[key]
                elif key == 'guanzhu_discount':
                    json['guanzhu_discount'] = rest[key]['message']
                elif key == 'dishes_discount':
                    json['dishes_discount'] = rest[key]['message']
                elif key == 'business_dist':
                    json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                    json['business_name'] = rest[key][0]['name']
                elif key == 'guide_image':
                    json['guide_image'] = rest[key]
                elif key == 'address':
                    json['address'] = rest[key]
                elif key == 'wine_discount':
                    json['wine_discount'] = rest[key]['message']
                elif key == 'zuobiao':
                    json['distance'] = u'未知'
                else:
                    pass
            list.append(json)
    return list
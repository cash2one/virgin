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
    item = mongo.coupons.find({'button':'0','restaurant_id':ObjectId(restaurant_id),'kind':kind,'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()}}).sort("showtime_start", pymongo.DESCENDING)[0:1]
    json = {
        'id':'',
        'content':''
    }
    for i in item:
        json['id'] = str(i['_id'])
        if i['type'] == '1':
            if i['rule'] == '0':
                json['content'] = '下单即减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '1':
                json['content'] = '全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '2':
                json['content'] = '菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '3':
                json['content'] = '酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            else:
                pass
        elif i['type'] == '2':
            if i['rule'] == '0':
                json['content'] = '下单即打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '1':
                json['content'] = '全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '2':
                json['content'] = '菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '3':
                json['content'] = '酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            else:
                pass
        else:
            json['content'] = i['content']
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
#获取用户1是0否关注饭店
def getconcern(restaurant_id,webuser_id):
    try:
        item = mongo.concern.find({"restaurant_id":ObjectId(restaurant_id),"webuser_id":ObjectId(webuser_id)})
    except:
        return '0'
    status = '0'
    for i in item:
        status = '1'
    return status
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
#根据经纬度查询所在商圈
def business_dist(lon1=126.593666, lat1=45.706477):
    pass
    item = mongo.district.find({},{"biz_areas":1})
    biz_areas_list = []
    for i in item:
        for j in i['biz_areas']:
            biz_areas_list.append((int(haversine(lon1=lon1,lat1=lat1,lon2=j['longitude'],lat2=j['latitude'])),j['biz_area_id'],j['biz_area_name']))
    return sorted(biz_areas_list)[0][0],sorted(biz_areas_list)[0][1],sorted(biz_areas_list)[0][2]
#根据获取的经纬度查询若干条距离最近的饭店信息
def guess(first={},lat1=45.76196769636328,lon1=126.65381534034498,start=0,end=3,webuser_id='5770c183dcc88e6506b95225'):
    if lat1!='y':
        item = mongo.restaurant.find(first,{"zuobiao":1})
        rsetaurant_list = []
        for i in item:
            try:
                rsetaurant_list.append((int(haversine(float(lon1), float(lat1), i['zuobiao'][0]['c1'], i['zuobiao'][0]['c2'])), str(i['_id'])))
            except:
                print i
        list=[]
        for l in sorted(rsetaurant_list)[start:end]:
            restaurant = mongo.restaurant.find({'_id':ObjectId(l[1])})

            for rest in restaurant:
                json = {}
                for key in rest.keys():
                    if key == '_id':
                        json['id'] = str(rest[key])
                        # json['kind1'] = getcoupons('1',rest[key])['content']
                        # json['kind2'] = getcoupons('2',rest[key])['content']
                        # json['kind3'] = getcoupons('3',rest[key])['content']
                        json['kind1'] = '满多少打多少折'
                        json['kind2'] = '满多少减多少元'
                        json['kind3'] = '任性就是送'
                        json['concern'] =getconcern(rest[key],webuser_id)
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(rest[key])
                    elif key == 'name':
                        json['name'] = rest[key]
                    elif key == 'restaurant_discount':
                        json['restaurant_discount'] = rest[key]['message']
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
                    # json['kind1'] = getcoupons('1',rest[key])['content']
                    # json['kind2'] = getcoupons('2',rest[key])['content']
                    # json['kind3'] = getcoupons('3',rest[key])['content']
                    json['kind1'] = '满多少打多少折'
                    json['kind2'] = '满多少减多少元'
                    json['kind3'] = '任性就是送'
                    json['concern'] =getconcern(rest[key],webuser_id)
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
#查询所有行政区标签
def district_list(first={}):
    item = mongo.district.find(first,{"district_name":1})
    list = []
    for i in item:
        data = {}
        data['id'] = str(i['_id'])
        data['district_name'] = i['district_name']
        list.append(data)
    return list
#根据行政区标签查询商圈
def business_dist_byid(id):
    item = mongo.district.find({'_id':ObjectId(id)},{"biz_areas":1})
    data = {}
    for i in item:
        for key in i.keys():
            if key == '_id':
                pass
            else:
                list = []
                for j in i[key]:
                    data2 = {}
                    for k in j.keys():
                        data2[k] = str(j[k])
                    list.append(data2)
                data[key] = list
    return data
if __name__ == '__main__':
    pass
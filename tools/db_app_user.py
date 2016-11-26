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
def getcoupons(kind, restaurant_id, flag='1'):
    if kind == '1':
        title = '关注享：'
    elif kind == '2':
        title = '新粉享：'
    else:
        title = '抢优惠：'
    item = mongo.coupons.find({"$or":[{"button":"0"}, {"button":0}],'restaurant_id':ObjectId(restaurant_id),'kind':kind,'showtime_start': {'$lt': datetime.datetime.now()},'showtime_end': {'$gte': datetime.datetime.now()}}).sort("showtime_start", pymongo.DESCENDING)[0:1]
    json = {
        'id':'',
        'content':'',
        'num':''
    }
    if flag == '0':
        json['time'] = ''
    for i in item:
        json['id'] = str(i['_id'])
        if int(i['num']) != -1:
            json['num'] = str(i['num'])
        else:
            json['num'] = ''
        if i['type'] == '1':
            if i['rule'] == '0':
                json['content'] = title+'下单即减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '1':
                json['content'] = title+'全品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '2':
                json['content'] = title+'菜品满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            elif i['rule'] == '3':
                json['content'] = title+'酒类满'+str(i['money'])+'元'+'减'+str(i['cross-claim'])+'元'
            else:
                pass
        elif i['type'] == '2':
            if i['rule'] == '0':
                json['content'] = title+'下单即打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '1':
                json['content'] = title+'全品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '2':
                json['content'] = title+'菜品满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            elif i['rule'] == '3':
                json['content'] = title+'酒类满'+str(i['money'])+'元'+'打'+str(i['cross-claim'])+'折'
            else:
                pass
                pass
        else:
            json['content'] = i['content']
        if flag == '0':
            json['time'] = i['indate_start'].strftime('%Y年%m月%d日') +"-"+ i['indate_end'].strftime('%Y年%m月%d日')

    return json
#获取首页店粉优惠大图
def getimg(restaurant_id):
    item = mongo.restaurant.find({"_id":ObjectId(restaurant_id)},{'guide_image':1})
    img = ""
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
def getxingzhengqu_id(xid):
    item = mongo.district.find({"biz_areas.biz_area_id":int(xid)},{"_id":1})
    for i in item:
        return str(i["_id"])
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
def guess(first={},lat1=45.76196769636328,lon1=126.65381534034498,start=0,end=3,webuser_id=''):
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
                        json['kind1'] = getcoupons('1',rest[key])['content']
                        json['kind2'] = getcoupons('2',rest[key])['content']
                        json['kind3'] = getcoupons('3',rest[key])['content']
                        # json['kind1'] = '满多少打多少折'
                        # json['kind2'] = '满多少减多少元'
                        # json['kind3'] = '任性就是送'
                        if webuser_id !='-1':
                            json['concern'] =getconcern(rest[key],webuser_id)
                        else:
                            json['concern'] = "0"
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(rest[key])
                    elif key == 'name':
                        json['name'] = rest[key]
                    elif key == 'restaurant_discount':
                        json['restaurant_discount'] = rest[key]['message']
                    elif key == 'guanzhu_discount':
                        json['guanzhu_discount'] = rest[key]['message']
                    elif key == 'dishes_discount':
                        json['dishes_discount'] = rest[key]['message']
                    elif key == 'business_dist':
                        json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                        json['district_id'] = getxingzhengqu_id(rest[key][0]['id'])
                        json['business_name'] = rest[key][0]['name']
                    elif key == 'guide_image':
                        json['guide_image'] = rest[key]
                    elif key == 'address':
                        json['address'] = rest[key]
                    elif key == 'wine_discount':
                        json['wine_discount'] = rest[key]['message']
                    elif key == 'fendian':
                        if rest[key] != {}:
                            json['liansuo'] = '1'
                        else:
                            json['liansuo'] = '0'
                    else:
                        if l[0] >100:
                            json['distance'] = str(float(l[0])/1000)[0:3]+'km'
                        else:
                            json['distance'] = str(l[0])+'m'
                        json['menutype'] = '0'
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
                    # json['kind1'] = '满多少打多少折'
                    # json['kind2'] = '满多少减多少元'
                    # json['kind3'] = '任性就是送'
                    if webuser_id !='-1':
                        json['concern'] =getconcern(rest[key],webuser_id)
                    else:
                        json['concern'] = "0"
                elif key == 'restaurant_id':
                    json['restaurant_id'] = str(rest[key])
                elif key == 'name':
                    json['name'] = rest[key]
                elif key == 'restaurant_discount':
                        json['restaurant_discount'] = rest[key]['message']
                elif key == 'guanzhu_discount':
                    json['guanzhu_discount'] = rest[key]['message']
                elif key == 'dishes_discount':
                    json['dishes_discount'] = rest[key]['message']
                elif key == 'business_dist':
                    json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                    json['district_id'] = getxingzhengqu_id(rest[key][0]['id'])
                    json['business_name'] = rest[key][0]['name']
                elif key == 'guide_image':
                    json['guide_image'] = rest[key]
                elif key == 'address':
                    json['address'] = rest[key]
                elif key == 'wine_discount':
                    json['wine_discount'] = rest[key]['message']
                elif key == 'zuobiao':
                    json['distance'] = ''
                elif key == 'fendian':
                    if rest[key] != {}:
                        json['liansuo'] = '1'
                    else:
                        json['liansuo'] = '0'
                else:
                    pass
            list.append(json)
    return list
#查询所有行政区标签
def district_list(first={}):
    first = {"_id":{"$in":[ObjectId("56d7af296bff8928c07855dc"),ObjectId("5643898b4be1e3bc3c3cd7ff"),ObjectId("5643898b4be1e3bc3c3cd801"),
                           ObjectId("56d9159b6bff84f2c02970d0"),ObjectId("56d93f810f884d063cdc9b0e"),ObjectId("56d93f810f884d063cdc9b0f"),]}}
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
#更新点菜菜单里的价格
def checkdish(webuser_id='57396ec17c1f31a9cce960f4'):
    order = mongo.order.find({'webuser_id':ObjectId(webuser_id),'status':8})
    for o in order:
        order_dict = o
        restaurant_id = o['restaurant_id']
        restaurant = mongo.restaurant.find({'_id':ObjectId(restaurant_id)})
        restaurant_dict = {}
        for r in restaurant:
            restaurant_dict = r
        dish_list = []
        wine_list = []
        for menu in restaurant_dict['menu']:
            if menu['dishs'] != [] and menu['dish_type'] == '1':
                for dish in menu['dishs']:
                    if menu['name'] != '酒水':
                        pass
                        for preset_dishs in order_dict['preset_dishs']:
                            if dish['id'] == preset_dishs['id']:
                                dish_dict = {}
                                dish_dict['name'] = dish['name']
                                dish_dict['price'] = float(dish['price'])
                                dish_dict['discount_price'] = float(dish['discount_price'])
                                dish_dict['num'] = int(preset_dishs['num'])
                                dish_dict['id'] = preset_dishs['id']
                                dish_list.append(dish_dict)
                    else:
                        for preset_wine in order_dict['preset_wine']:
                            if dish['id'] == preset_wine['id']:
                                dish_dict = {}
                                dish_dict['name'] = dish['name']
                                dish_dict['price'] = float(dish['price'])
                                dish_dict['discount_price'] = float(dish['discount_price'])
                                dish_dict['num'] = int(preset_wine['num'])
                                dish_dict['id'] = preset_wine['id']
                                wine_list.append(dish_dict)
        mongo.order.update_one({"restaurant_id":ObjectId(restaurant_id),"webuser_id":ObjectId(webuser_id),"status":8},{"$set": {"preset_dishs":dish_list,"preset_wine": wine_list}})
def coupons_by(first={}):
    item = mongo.coupons.find(first)
    json = {}
    for i in item:
        for key in i.keys():
            if key == '_id':
                json['id'] = str(i[key])
            elif key == 'restaurant_id':
                json['restaurant_id'] = str(i[key])
            elif key == 'kind':
                if i[key] == '1' or i[key] == '2':
                    json['button'] = i[key]
            elif key == 'rule':
                if i[key] == '0':
                    json['rule'] = i[key]
                    json['rulename'] = '无门槛'
                elif i[key] == '1':
                    json['rule'] = i[key]
                    json['rulename'] = '全品满'+str(i['money'])+'元可使用'
                elif i[key] == '2':
                    json['rule'] = i[key]
                    json['rulename'] = '菜品满'+str(i['money'])+'元可使用'
                elif i[key] == '3':
                    json['rule'] = i[key]
                    json['rulename'] = '酒类满'+str(i['money'])+'元可使用'
                else:
                    json['rule'] = ''
            elif key == 'content':
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
            elif key == 'showtime_start':
                json['showtime_start'] = i[key].strftime('%Y年%m月%d日')
            elif key == 'showtime_end':
                json['showtime_end'] = i[key].strftime('%Y年%m月%d日')
            elif key == 'indate_start':
                json['indate_start2'] = i[key]
                json['indate_start'] = i[key].strftime('%Y年%m月%d日')
            elif key == 'indate_end':
                json['indate_end2'] = i[key]
                json['indate_end'] = i[key].strftime('%Y年%m月%d日')
            elif key == 'addtime':
                json['addtime'] = i[key].strftime('%Y年%m月%d日')
            else:
                json[key] = i[key]
            if datetime.datetime.now()<i['indate_start']:
                    json['status'] = '未开始'
            elif i['indate_start']<datetime.datetime.now()<i['indate_end']:
                json['status'] = '进行中'
            else:
                json['status'] = '已结束'
            if i['num'] != -1:
                json['num'] = i['num']
            else:
                json['num'] = -1
    return json
def use_coupons(total = 50.0,dish_total = 40.0,wine_total = 10.0,restaurant_id='57329e300c1d9b2f4c85f8e6',webuser_id='57396fd67c1f31a9cce960f8'):
    finel = []
    # total = 50
    # dish_total = 40
    # wine_total = 10
    kind1 = []
    guanzhu = mongo.coupons.find({"restaurant_id":ObjectId(restaurant_id),"$or":[{"button":"0"}, {"button":0}],"kind":"1"})
    for g in guanzhu:
        if g['type'] == '1':
            kind1 = [g['cross-claim'],'1','0',str(g['_id'])]
        elif g['type'] == '2':
            kind1 = [total - total * g['cross-claim'],'2',g['rule'],g['money'],str(g['_id'])]
        else:
            kind1 = []
    mycoupons_list = []
    mycoupons = mongo.mycoupons.find({"webuser_id": ObjectId(webuser_id),
                                 "restaurant_id": ObjectId(restaurant_id)})
    for m in mycoupons:
        mycoupons_list.append(ObjectId(m['coupons_id']))
    print 'mycoupons_list',mycoupons_list
    list = []
    coupons = mongo.coupons.find({"_id":{"$in":mycoupons_list},"$or":[{"button":"0"}, {"button":0}],"type":{"$in":["1","2"]}})
    for c in coupons:
        print c
        if c['indate_start']<datetime.datetime.now()<c['indate_end']:
            if c['type'] == '1':
                list.append([c['cross-claim'],'1',c['rule'],c['money'],str(c['_id'])])
            else:
                list.append([total - total * c['cross-claim'],'2',c['rule'],c['money'],str(c['_id'])])
        else:
            pass
    print 'kind1', kind1
    print 'sorted(list,reverse=1)',sorted(list,reverse=1)
    list = sorted(list,reverse=1)
    if kind1 !=[]:
        if kind1[2] == '0':
            finel.append(kind1)
        elif kind1[2] == '1' and kind1[3]<=total:
            finel.append(kind1)
        elif kind1[2] == '2' and kind1[3]<=dish_total:
            finel.append(kind1)
        elif kind1[2] == '3' and kind1[3]<=wine_total:
            finel.append(kind1)
        else:
            pass
        if kind1[1] == '2':
            for l in list:
                if l[1] == '1':
                    if l[2] == '0':
                        # print l[0]
                        finel.append(l)
                        break
                    elif l[2] == '1' and l[3]<=total:
                        # print l[0]
                        finel.append(l)
                        break
                    elif l[2] == '2' and l[3]<=dish_total:
                        # print l[0]
                        finel.append(l)
                        break
                    elif l[2] == '3'and l[3]<=wine_total:
                        # print l[0]
                        finel.append(l)
                        break
                    else:
                        pass
        else:
            for l in list:
                if l[2] == '0':
                    # print l[0]
                    finel.append(l)
                    break
                elif l[2] == '1' and l[3]<=total:
                    # print l[0]
                    finel.append(l)
                    break
                elif l[2] == '2' and l[3]<=dish_total:
                    # print l[0]
                    finel.append(l)
                    break
                elif l[2] == '3'and l[3]<=wine_total:
                    # print l[0]
                    finel.append(l)
                    break
                else:
                    pass
    else:
        for l in list:
            if l[2] == '0':
                # print l[0]
                finel.append(l)
                break
            elif l[2] == '1' and l[3]<=total:
                # print l[0]
                finel.append(l)
                break
            elif l[2] == '2' and l[3]<=dish_total:
                # print l[0]
                finel.append(l)
                break
            elif l[2] == '3'and l[3]<=wine_total:
                # print l[0]
                finel.append(l)
                break
            else:
                pass
    # print finel
    tishi = ''
    print list
    for l in list:
        if l[2] == '1' and l[3]>total:
            if l[1] == '1':
                tishi = '提示：再加'+ str(l[3]-total)+'元就能减'+str(l[0])+'元'
            else:
                tishi = '提示：再加'+ str(l[3]-total)+'元就能打'+str(l[0])+'折'
            break
        elif l[2] == '2' and l[3]>dish_total:
            if l[1] == '1':
                tishi = '提示：再加'+ str(l[3]-total)+'元就能减'+str(l[0])+'元'
            else:
                tishi = '提示：再加'+ str(l[3]-total)+'元就能打'+str(l[0])+'折'
            break
        elif l[2] == '3'and l[3]>wine_total:
            if l[1] == '1':
                tishi = '提示：再加'+ str(l[3]-total)+'元就能减'+str(l[0])+'元'
            else:
                tishi = '提示：再加'+ str(l[3]-total)+'元就能打'+str(l[0])+'折'
            break
        else:
            pass
    return tishi,finel
def hobby(first={},lat1=None,lon1=None,start=0,end=3):
    if lat1!='y':
        print first
        item = mongo.restaurant.find(first,{"zuobiao":1})
        rsetaurant_list = []
        for i in item:
            try:
                rsetaurant_list.append((int(haversine(float(lon1), float(lat1), i['zuobiao'][0]['c1'], i['zuobiao'][0]['c2'])), str(i['_id'])))
            except:
                print i
        list=[]
        print rsetaurant_list
        for l in sorted(rsetaurant_list)[start:end]:
            restaurant = mongo.restaurant.find({'_id':ObjectId(l[1])})

            for rest in restaurant:
                json = {}
                for key in rest.keys():
                    if key == '_id':
                        json['id'] = str(rest[key])
                    elif key == 'restaurant_id':
                        json['restaurant_id'] = str(rest[key])
                    elif key == 'dishes_discount':
                        json['dishes_discount'] = rest[key]['message']
                    elif key == 'business_dist':
                        json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                        json['business_name'] = rest[key][0]['name']
                    elif key == 'wine_discount':
                        json['wine_discount'] = rest[key]['message']
                    elif key == 'address':
                        json['address'] = rest[key]
                    elif key == 'guide_image':
                        json['guide_image'] = rest[key]
                    elif key == 'name':
                        json['name'] = rest[key]
                    else:
                        # json['distance'] = l[0]
                        if l[0] >100:
                            json['distance'] = str(float(l[0])/1000)[0:3]+'km'
                        else:
                            json['distance'] = str(l[0])+'m'
                list.append(json)
    else:
        restaurant = mongo.restaurant.find(first).sort("addtime", pymongo.DESCENDING)[start:end]
        list = []
        for rest in restaurant:
            json = {}
            for key in rest.keys():
                print '11111111111'
                if key == '_id':
                    json['id'] = str(rest[key])
                elif key == 'restaurant_id':
                    json['restaurant_id'] = str(rest[key])
                elif key == 'dishes_discount':
                    json['dishes_discount'] = rest[key]['message']
                elif key == 'business_dist':
                    json['district_name'] = getxingzhengqu(rest[key][0]['id'])
                    json['business_name'] = rest[key][0]['name']
                elif key == 'wine_discount':
                    json['wine_discount'] = rest[key]['message']
                elif key == 'zuobiao':
                    json['distance'] = ''
                elif key == 'address':
                    json['address'] = rest[key]
                elif key == 'guide_image':
                    json['guide_image'] = rest[key]
                elif key == 'name':
                    json['name'] = rest[key]
            list.append(json)
    return list
if __name__ == '__main__':
    pass
    # print json_util.dumps(guess(),ensure_ascii=False,indent=2)
    # json = guess({"_id":{"$in":[ObjectId("57329e300c1d9b2f4c85f8e6")]}}, lat1='y', lon1='x', end=10,webuser_id='573feadf7c1fa8a326a9c03c')
    # for j in json:
    #     del j['distance']
    #     del j['liansuo']
    #     del j['business_name']
    #     del j['district_name']
    # print json_util.dumps(json,ensure_ascii=False,indent=2)
    # json = getcoupons('3','57329e300c1d9b2f4c85f8e6')
    # print json_util.dumps(json,ensure_ascii=False,indent=2)

    # list = []
    # for d in district_list():
    #     json = {}
    #     json['district_name'] = d['district_name']
    #     json['district_list'] = business_dist_byid(d['id'])
    #     list.append(json)
    # list = coupons_by({"restaurant_id":ObjectId("57329e300c1d9b2f4c85f8e6"),"kind":"2","button":"0"})
    # print json_util.dumps(list,ensure_ascii=False,indent=2)
    # print json_util.dumps(use_coupons(total = 50.0,dish_total = 40.0,wine_total = 10.0,restaurant_id='57329e300c1d9b2f4c85f8e6',webuser_id='57396ec17c1f31a9cce960f4'),ensure_ascii=False,indent=2)
    print getimg('5816e7fb0c1d9bd5630b4f85')
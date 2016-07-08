# coding=utf-8
import json
import os
import base64
from io import BytesIO

# import qrcode as qrc
import datetime
import random

import requests
from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler
import urllib2
import re
from flask import request, Response

import connect
from connect import conn,settings
from bson import ObjectId,json_util
import sys
reload(sys)
sys.setdefaultencoding('utf8')
mongo=conn.mongo_conn()
mongouser=conn.mongo_conn_user()
def return_json(code,message,jwt,data):
    if jwt:
        data = data
    else:
        data = {"jwt":"field"}
    json={
        "code":code,
        "message":message,
        "auto":jwt,
        "data": data
    }
    return json


def orderformate(pdict={},table={}):
    pdict = dict(filter(lambda x:x[1]!='', pdict.items()))
    data = formatp(pdict,table)
    return data
    pass

def formatp(data,table):
    for key in data.keys():
        data[key]=format_type(data[key], table[key])
    return data

def format_type(data, type):
    if type == 'str':
        return str(data)
    elif type == 'int':
        return int(data)
    elif type == 'obj':
        return ObjectId(data)
    elif type == 'boo':
        return bool(data)
    elif type == 'flo':
        return float(data)
    else:
        return data
    pass
def json_value(json_data, key_name, dump=False):
    if json_data is None:
        return None
    if key_name in json_data.keys():
        if dump:
            return json.dumps(json_data[key_name])
        else:
            return json_data[key_name]
    else:
        return None


class Restaurant:
    def __init__(self, ident_json):
        self.ident = ident_json
        self.data, self.obj_id = self.__find_item()
        self.dish_data = None
        self.menu_data = None
        self.info_data = None
        self.add_dish_data = None
        self.new_menu = None

    def __find_item(self):
        if '_id' in self.ident:
            f = {"_id": ObjectId(self.ident['_id'])}
        elif 'menu_id' in self.ident:
            f = {"menu.id": self.ident['menu_id']}
        elif 'dish_id' in self.ident:
            f = {"menu.dishs.id": self.ident['dish_id']}
        elif 'admin_id' in self.ident:
            f = {"user": {"$in": [ObjectId(self.ident['admin_id'])]}}
        else:
            return None, ''
        found = json_util.loads(json_util.dumps(mongo.restaurant.find_one(f)))
        return found, '' if found is None else str(found['_id'])

    def info(self, key=None):
        if self.data is None:
            # print 'Noting in db'
            return None
        need = None
        if '_id' in self.ident:
            need = self.data
        elif 'menu_id' in self.ident:
            for menu in self.data['menu']:
                if menu['id'] == self.ident['menu_id']:
                    need = menu
        elif 'dish_id' in self.ident:
            for menu in self.data['menu']:
                if menu['dish_type'] == '1':
                    for dish in menu['dishs']:
                        if str(dish['id']) == str(self.ident['dish_id']):
                            need = dish
        else:
            print 'Not Support input ident'
            need = None
        if key:
            if need:
                return need[key]
            else:
                return None
        else:
            return need

    def get_item(self, key_name):
        if self.data is None:
            print 'Data ERROR'
            return None
        else:
            if key_name == '_id':
                return self.obj_id
            elif key_name in self.data.keys():
                return self.data[key_name]
            else:
                'KeyName Error'
                return None

    def add_dish(self, dish_data=None):
        self.add_dish_data = dish_data

    def re_dish(self, dish_data=None):
        self.dish_data = dish_data

    def re_menu(self, menu_data=None):
        self.menu_data = menu_data

    def re_infos(self, info_data=None):
        self.info_data = info_data

    def rebuild(self):
        if self.new_menu is None:
            rebuild_data = self.data
        else:
            rebuild_data = self.new_menu
        menu_list = []
        for menu in rebuild_data['menu']:  # 循环数据库的菜单
            new_menu = dict()
            for key in menu.keys():  # 循环菜单的键名
                if key == 'dishs':  # 如果是菜品列表
                    dishs = []
                    for dish in menu['dishs']:  # 循环菜单中的菜品
                        try:
                            if dish['id'] in self.dish_data.keys():  # 判断是否是需要修改的菜品
                                dish_new = {}
                                for key_name in dish.keys():  # 循环菜品包含的键名
                                    if key_name in self.dish_data[dish['id']].keys():  # 如果是需要修改的键
                                        dish_new[key_name] = self.dish_data[dish['id']][key_name]
                                    else:  # 如果不需要修改
                                        dish_new[key_name] = dish[key_name]
                                dishs.append(dish_new)
                            else:  # 不是要修改的菜品
                                dishs.append(dish)
                        except Exception, e:
                            print e
                            dishs.append(dish)
                    if self.add_dish_data:
                        if menu['id'] in self.add_dish_data.keys():  # 如果当前菜单是需要添加菜品的菜单
                            for new_dish in self.add_dish_data[menu['id']]:  # 循环操作添加新菜品
                                dishs.append(new_dish)
                    new_menu['dishs'] = dishs
                else:  # 如果是菜单信息
                    if self.menu_data is not None and (menu['id'] in self.menu_data.keys()):
                        if key in self.menu_data[menu['id']].keys():
                            new_menu[key] = self.menu_data[menu['id']][key]
                        else:
                            new_menu[key] = menu[key]
                    else:
                        new_menu[key] = menu[key]
            menu_list.append(new_menu)
        self.new_menu = {'menu': menu_list}
        return True

    def submit2db(self):
        if self.new_menu is None:
            self.rebuild()
        try:
            update = self.info_data
            if self.new_menu:
                update['menu'] = self.new_menu['menu']
            mongo.restaurant.update_one({"_id": ObjectId(self.obj_id)},
                                        {"$set": update})
            return True
        except Exception, e:
            print e
            return False


class Discount:
    def __init__(self, objid):
        self.objid = {"_id": ObjectId(objid)}
        self.data = self.__get_db_data()
        self.dish_data = None
        self.menu_data = None
        self.new_menu = None
        self.add_dish_data = None
    def rebuild(self):
        if self.new_menu is None:
            rebuild_data = self.data
        else:
            rebuild_data = self.new_menu
        menu_list = []
        for menu in rebuild_data['menu']:
            new_menu = dict()
            for key in menu.keys():
                if key == 'dishs':
                    dishs = []
                    if menu['name'] !='优惠菜' and menu['name'] !='推荐菜' and menu['dish_type'] =='1' and menu['dishs']!=[]:
                        for dish in menu['dishs']:
                            try:
                                if 'id' in dish.keys():
                                    if dish['id'] in self.dish_data.keys():
                                        dish_new = {}
                                        for key_name in dish.keys():
                                            if key_name in self.dish_data[dish['id']].keys():
                                                dish_new[key_name] = self.dish_data[dish['id']][key_name]
                                            else:
                                                dish_new[key_name] = dish[key_name]
                                        dishs.append(dish_new)
                                    else:
                                        dishs.append(dish)
                                else:
                                    dishs.append(dish)
                            except Exception, e:
                                dishs.append(dish)
                                pass
                        if self.add_dish_data:
                            if menu['id'] in self.add_dish_data.keys():  # 如果当前菜单是需要添加菜品的菜单
                                for new_dish in self.add_dish_data[menu['id']]:  # 循环操作添加新菜品
                                    dishs.append(new_dish)
                        new_menu['dishs'] = dishs
                    else:
                        new_menu[key] = menu[key]
                else:
                    if self.menu_data is not None and (menu['id'] in self.menu_data.keys()):
                        if key in self.menu_data[menu['id']].keys():
                            new_menu[key] = self.menu_data[menu['id']][key]
                        else:
                            new_menu[key] = menu[key]
                    else:
                        new_menu[key] = menu[key]
            menu_list.append(new_menu)
        self.new_menu = {'menu': menu_list}
        return True

    def re_dish(self, dish_data=None):
        self.dish_data = dish_data
    def add_dish(self, dish_data=None):
        self.add_dish_data = dish_data
    def re_menu(self, menu_data=None):
        self.menu_data = menu_data

    def __get_db_data(self):
        return mongo.restaurant.find(self.objid, {"menu": 1})[0]

    def submit2db(self):
        if self.new_menu is None:
            self.rebuild()
        try:
            mongo.restaurant.update_one(self.objid, {"$set": self.new_menu})
            return True
        except Exception, e:
            return False

def pimg(uu):
  # try:
    #创建一个请求
    handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler]
    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)
    # 打开图片
    cc = open(uu, "rb")
    datagen, headers = multipart_encode({"image": cc })
    #发送请求
    request = urllib2.Request(settings.setimageIP , datagen, headers)
    request = urllib2.Request(settings.setimageIP1 , datagen, headers)
    #测试本地用
    # request = urllib2.Request(settings.setimageIPlocal , datagen, headers)

    #获取返回中的内容
    re1 = r"<h1>MD5:(?P<md5>.*?)</h1>"
    match5 = re.findall(re1,urllib2.urlopen(request).read())
    a = match5[0]
    cc.close()
    print str(a).replace(" ","")
    return str(a).replace(" ","")
  # except Exception, e:
  #       return e


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


# correction_levels = {
#     'L': qrc.constants.ERROR_CORRECT_L,
#     'M': qrc.constants.ERROR_CORRECT_M,
#     'Q': qrc.constants.ERROR_CORRECT_Q,
#     'H': qrc.constants.ERROR_CORRECT_H
# }
def qrcode(data, version=None, error_correction='L', box_size=10, border=0, fit=True):
    """ makes qr image using qrcode as qrc See documentation for qrcode package for info"""
    # qr = qrc.QRCode(
    #     version=version,
    #     error_correction=correction_levels[error_correction],
    #     box_size=box_size,
    #     border=border
    # )
    # qr.add_data(data)
    # qr.make(fit=fit)
    #
    # # creates qrcode base64
    # out = BytesIO()
    # qr_img = qr.make_image()
    # filename = '%s%s' % (gen_rnd_filename(), ".PNG")
    # # osstr = os.path.dirname(__file__).replace("tools","")+"static/upload/"+filename
    # osstr = "/www/site/foodmap/virgin/virgin/static/upload/"+filename
    osstr = "/www/site/foodmap/virgin/virgin/static/upload/head.png"
    # qr_img.save(osstr)
    uu = pimg(osstr)
    # u1 = settings.getimageIP + str(uu)
    # os.remove(osstr)
    return uu



#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
def tuisong(mfrom='', mto='', title='', info='',goto='',channel='',type='',
            appname='',msgtype='',target='',ext='', ispush=True):
    baseurl = 'http://127.0.0.1:10035'
    androidreq = {}
    iosreq = {}
    try:
        #以下是获取消息来源名
        infofromname = ''
        if type == '0':
            item = mongo.webuser.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['nickname']
        elif type == '1':
            item = mongo.restaurant.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['name']
        elif type == '2':
            item = mongo.webuser.find({"_id":ObjectId(mfrom)})
            for i in item:
                infofromname = i['nickname']
        else:
            pass
            infofromname = '未知'
        #获取消息来源名结束


        #本地消息表接收方id
        infoto = {}
        #安卓设备号数组
        identandroid = ''
        identandroidlist = []
        #IOS设备号数组
        identios = ''
        identioslist = []
        if mto!='':
            idlist = mto.split('_')
            for mid in idlist:
                if mid != '' and mid != None:
                    infoto[mid] = 0
                    #mid是接收方id 下面webuser是查询用户中心id
                    webuser = mongo.webuser.find({"_id":ObjectId(mid)})
                    for w in webuser:
                        #查询用户中心表usercenter得到设备类型和设备号
                        usercenter = mongouser.user_web.find({"_id":ObjectId(w['automembers_id'])})
                        for u in usercenter:
                            #0是安卓1是IOS
                            if u['lastlogin']['type'] == '0':
                                #拼接TargetValue参数
                                identandroidlist.append(identandroid+u['lastlogin']['ident'])
                            else:
                                identioslist.append(identandroid+u['lastlogin']['ident'])
        identandroid = ",".join(identandroidlist)
        identios = ",".join(identioslist)
        print identandroid,identios
        issave = True
        #阿里网关参数安卓
        androidmsg = {}
        #阿里网关参数IOS
        iosmsg = {}
        #阿里网关返回参数

        #target是all表示发送给所有设备
        if target=='device':
            #message是消息
            if msgtype == 'message':
                #分别判断设备号数组串，为空就不能发
                if identandroid!='' and ispush:
                    #固定模板
                    androidmsg = {"appname": appname, "type": msgtype, "Message": info, "Target": "device", "TargetValue": identandroid}
                    #requests方式POST
                    androidreq = requests.post(baseurl+'/push.android',data=androidmsg).json()
                    issave = androidreq['success']
                    if androidreq['success']:
                        print '安卓消息个推推送成功！'
                    else:
                        print '安卓消息个推推送失败！原因'+str(androidreq['Message'])
                if identios!='' and ispush:
                    iosmsg = {"appname": appname, "type": msgtype, "Message": info, "Summary": title, "Target": "device", "TargetValue": identios}
                    iosreq = requests.post(baseurl+'/push.ios',data=iosmsg).json()
                    issave = iosreq['success']
                    if iosreq['success']:
                        print 'IOS消息个推推送成功！'
                    else:
                        print 'IOS消息个推推送失败！原因'+str(iosreq['Message'])
            #notice是通知
            else:

                if identandroid!='' and ispush:
                    androidmsg = {"appname": appname, "type": msgtype, "Title": title, "Summary": "1", "Target": "device", "TargetValue": identandroid,"ext":ext}
                    androidreq = requests.post(baseurl+'/push.android',data=androidmsg).json()
                    issave = androidreq['success']
                    if androidreq['success']:
                        print '安卓通知个推推送成功！'
                    else:
                        print '安卓通知个推推送失败！原因'+str(androidreq['Message'])
                print identios!='' and ispush
                if identios!='' and ispush:
                    iosmsg = {"appname": appname, "type": msgtype, "Summary": title, "Target": "device", "TargetValue": identios,"ext":ext}
                    iosreq = requests.post(baseurl+'/push.ios',data=iosmsg).json()
                    issave = iosreq['success']
                    if iosreq['success']:
                        print 'IOS通知个推推送成功！'
                    else:
                        print 'IOS通知个推推送失败！原因'+str(iosreq['Message'])
        elif target=='all':
            if msgtype == 'message':
                if ispush:
                    androidmsg = {"appname": appname, "type": msgtype, "Message": info, "Target": "all", "TargetValue": "all"}
                    androidreq = requests.post(baseurl+'/push.android',data=androidmsg).json()
                    issave = androidreq['success']
                    if androidreq['success']:
                        print '安卓消息全推推送成功！'
                    else:
                        print '安卓消息全推推送失败！原因'+str(androidreq['Message'])
                    iosmsg = {"appname": appname, "type": msgtype, "Message": info, "Summary": title, "Target": "all", "TargetValue": "all"}
                    iosreq = requests.post(baseurl+'/push.ios',data=iosmsg).json()
                    issave = iosreq['success']
                    if iosreq['success']:
                        print 'IOS消息全推推送成功！'
                    else:
                        print 'IOS消息全推推送失败！原因'+str(iosreq['Message'])
            else:
                if ispush:
                    androidmsg = {"appname": appname, "type": msgtype, "Title": title, "Summary": "1", "Target": "all", "TargetValue": "all","ext":ext}
                    androidreq = requests.post(baseurl+'/push.android',data=androidmsg).json()
                    issave = androidreq['success']
                    if androidreq['success']:
                        print '安卓通知全推推送成功！'
                    else:
                        print '安卓通知全推推送失败！原因'+str(androidreq['Message'])
                    iosmsg = {"appname": appname, "type": msgtype, "Summary": title, "Target": "all", "TargetValue": "all","ext":ext}
                    iosreq = requests.post(baseurl+'/push.ios',data=iosmsg).json()
                    issave = iosreq['success']
                    if iosreq['success']:
                        print 'IOS通知全推推送成功！'
                    else:
                        print 'IOS通知全推推送失败！原因'+str(iosreq['Message'])
        else:
            pass
        insertjson = {
                "infofrom" : ObjectId(mfrom),
                "infoto" : infoto,
                "infos" : {
                    "infotitle" : title,
                    "information" : info,
                    "infofromname" : infofromname
                },
                "type" : 0,
                "add_time" : datetime.datetime.now(),
                "goto":goto,
                "is_push":ispush,
                "channel":channel,
                "androidmsg" : androidmsg,
                "iosmsg": iosmsg
        }
        if issave:
            mongo.message.insert(insertjson)
            return True
        else:
            return False
    except:
        return False


def getdishsitem(restaurant_id):
     rent = mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"menu":1,"_id":0})
     dishs=[]
     for a in rent["menu"]:
         if str(a["name"]) !="优惠菜" and str(a["name"]) != "推荐菜" and int(a["dish_type"])==1:
             for b in a["dishs"]:
                 # print b
                 dishs.append(b)
     return dishs

def ceshi(restaurant_id):
                orderdishs=[]
                dishs =getdishsitem(str(restaurant_id))
                l=[]
                # print "dishs："
                # print len(dishs)
                b = random.randint(0,20)
                # print b
                for i in range(b):
                    x=random.randint(0,len(dishs)-1)
                    print x
                    if x in l:
                        continue #这样你就不会选到想同的数了！
                    else:
                        l.append(x)
                # print "l:"
                # print l
                for a in l:
                    orderdishs.append(dishs[int(a)])
                # print orderdishs
                # print len(orderdishs)
                return orderdishs

#修改order表中的全部信息
def testpreset_dishs():
    list=mongo.order.find({},{"preset_dishs":1})
    for a in list:
        l = a["preset_dishs"]
        list=[]
        for b in l:
            json={
                "name" : b["name"],
                "id" : b["id"],
                "price" : b["price"],
                "discount_price" : b["discount_price"],
                "num" : 1
            }
            list.append(json)
        mongo.order.update({"_id":a["_id"]},{"$set":{"preset_dishs":list}})
    return 1

def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

#给所有饭店包房增加 大厅
def adddating():

    ll = mongo.restaurant.find()
    c=1
    for a in ll:
        import time
        time.sleep(1)
        item = a["rooms"]
        json={}
        for i in item:
            if i["room_name"] == "大厅":
                json = i
                list = mongo.restaurant.update({"_id":a["_id"]},{"$pull":{"rooms":json}},False,False)
        json["room_people_name"] ="大厅"
        json["room_people_id"] = "108"
        list = mongo.restaurant.update_one({"_id":a["_id"]},{"$push":{"rooms":json}})
        print list
        c=c+1
        print c
    return 1

def test():
        aaa = mongo.restaurant.update_one({"_id":ObjectId("57329b1f0c1d9b2f4c85f8e3")},{"$push":{"rooms":{}}})
        print aaa.modified_count



if __name__ == '__main__':
    test()
    # testpreset_dishs()
    # ceshi("57340b330c1sd9b314998892f")
    # pass
    # print qrcode("测试")
    # dish = {
    #                 "is_enabled" : 'str',
    #                 "name" : "str",
    #                 "shijia" : 'boo',
    #                 "price" : 'flo',
    #                 "is_recommend" : 'boo',
    #                 "discount_price" : 'flo',
    #                 "summary" : "str",
    #                 "praise_num" : 'int',
    #                 "guide_image" : "str",
    #                 "type" : "str",
    #                 "id" : "str"
    #         }
    # obj = '57329b1f0c1d9b2f4c85f8e3'
    # test_dish = {
    #     '201605111118535612': {'discount_price': 66,'name': '111111111111111111111111111111111111111111111111'}, '201605111003381987': {'discount_price': 88}
    # }
    # test_menu = {
    #     '201605111118535612': {'name': '111111111111111111111111111111111111111111111111'}
    # }
    # test_add = {
    #     '201605111038236629': [{
    #                 "is_enabled" : True,
    #                 "name" : "1981肥牛王",
    #                 "shijia" : False,
    #                 "price" : 12.0,
    #                 "is_recommend" : True,
    #                 "danwei" : "",
    #                 "discount_price" : 55555555555.0,
    #                 "summary" : "",
    #                 "praise_num" : 0,
    #                 "guide_image" : "",
    #                 "type" : "0",
    #                 "id" : "201605111041429997"
    #             }]
    # }
    # # test_data = mongo.restaurant.find({"_id" : ObjectId("57327f4a8831ac0e5cb96404")},{"menu":1})[0]
    # # print json_util.dumps(test_data,ensure_ascii=False,indent=2)
    # # first = Foormat(obj)
    # # first.add_dish(test_add)
    # # first.re_dish(test_dish)
    # # first.re_menu(test_menu)
    # # print first.submit2db()
    # # print Restaurant({'dish_id': '201605111053268902'}).info
    # pass




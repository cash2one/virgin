# coding=utf-8
import sys

import requests
from bson import ObjectId

reload(sys)
sys.setdefaultencoding('utf8')
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import datetime
import logging
from connect import conn

# datetime.datetime.now()-datetime.timedelta(seconds = timeout * 60)
mongo = conn.mongo_conn()
mongouser = conn.mongo_conn_user()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='log1.txt',
                    filemode='a')


# 检查是否发送过此推送
def checkmsg(data_id='', goto=''):
    pass
    item = mongo.message.find({"data_id": data_id, "goto": goto})
    flag = True
    for i in item:
        flag = False
    return flag


# 根据包房id获取包房名
def getroom(id='', room_id=''):
    item = mongo.restaurant.find({"_id": ObjectId(id)})
    rnanme = ''
    for i in item:
        for r in i['rooms']:
            if room_id == r['room_id']:
                rnanme = r['room_name']
    return rnanme


def tuisong(mfrom='', mto='', title='', info='', goto='', channel='', type='', totype='',
            appname='', msgtype='', target='', ext='', ispush=True, data_id='-1'):
    ispush = False
    baseurl = 'http://127.0.0.1:10035'
    androidreq = {}
    iosreq = {}
    # try:
    # 以下是获取消息来源名
    infofromname = ''
    if type == '0':
        infofromname = '美食地图'
        mfrom = '580da84b87f89cf90e31a894'
        # item = mongo.webuser.find({"_id":ObjectId(mfrom)})
        # for i in item:
        #     infofromname = i['nickname']
    elif type == '1':
        item = mongo.restaurant.find({"_id": ObjectId(mfrom)})
        for i in item:
            infofromname = i['name']
    elif type == '2':
        item = mongo.webuser.find({"_id": ObjectId(mfrom)})
        for i in item:
            infofromname = i['nickname']
    else:
        pass
        infofromname = '未知'
    # 获取消息来源名结束


    # 本地消息表接收方id
    infoto = {}
    # 安卓设备号数组
    identandroid = ''
    identandroidlist = []
    # IOS设备号数组
    identios = ''
    identioslist = []
    if mto != '':
        idlist = mto.split('_')
        for mid in idlist:
            if mid != '' and mid != None:
                infoto[mid] = 0
                try:
                    # mid是接收方id 下面webuser是查询用户中心id,totype区分是谁接收，1是用户，查询用户表，0是商家，查询饭店表user字段
                    if totype == '1':
                        webuser = mongo.webuser.find({"_id": ObjectId(mid)})
                        for w in webuser:
                            # 查询用户中心表usercenter得到设备类型和设备号
                            usercenter = mongouser.user_web.find({"_id": ObjectId(w['automembers_id'])})
                            for u in usercenter:
                                # 0是安卓1是IOS
                                if u['lastlogin']['type'] == '0':
                                    # 拼接TargetValue参数
                                    identandroidlist.append(identandroid + u['lastlogin']['ident'])
                                else:
                                    identioslist.append(identandroid + u['lastlogin']['ident'])
                    else:
                        restaurant = mongo.restaurant.find({"_id": ObjectId(mid)})
                        for r in restaurant:
                            for usercenter_id in r['user']:
                                if usercenter_id != '' and usercenter_id != None:
                                    usercenter = mongouser.user_web.find({"_id": ObjectId(usercenter_id)})
                                    for u in usercenter:
                                        # 0是安卓1是IOS
                                        if u['lastlogin']['type'] == '0':
                                            # 拼接TargetValue参数
                                            identandroidlist.append(identandroid + u['lastlogin']['ident'])
                                        else:
                                            identioslist.append(identandroid + u['lastlogin']['ident'])
                                else:
                                    print '此饭店暂无管理员，获取不到接收方设备号'
                except  Exception, e:
                    print str(e) + '获取不到接收方设备号'
    identandroid = ",".join(identandroidlist)
    identios = ",".join(identioslist)
    print identandroid, identios
    issave = True
    # 阿里网关参数安卓
    androidmsg = {}
    # 阿里网关参数IOS
    iosmsg = {}
    # 阿里网关返回参数
    insertjson = {
        "infofrom": ObjectId(mfrom),
        "infoto": infoto,
        "infos": {
            "infotitle": title,
            "information": info,
            "infofromname": infofromname
        },
        "type": 0,
        "add_time": datetime.datetime.now(),
        "goto": goto,
        "is_push": ispush,
        "channel": channel,
        "androidmsg": androidmsg,
        "iosmsg": iosmsg
    }
    if data_id != '-1':
        insertjson['data_id'] = data_id
    else:
        insertjson['data_id'] = '-1'
    # if issave:
    mes = mongo.message.insert(insertjson)
    if goto == "5":
        ext = '{"goto":"5","id":"' + str(mes) + '"}'
    # target是all表示发送给所有设备
    if target == 'device':
        # message是消息
        if msgtype == 'message':
            # 分别判断设备号数组串，为空就不能发
            if identandroid != '' and ispush:
                # 固定模板
                androidmsg = {"appname": appname, "type": msgtype, "Message": info, "Target": "device",
                              "TargetValue": identandroid}
                # requests方式POST
                androidreq = requests.post(baseurl + '/push.android', data=androidmsg).json()
                issave = androidreq['success']
                if androidreq['success']:
                    print '安卓消息个推推送成功！'
                else:
                    print '安卓消息个推推送失败！原因' + str(androidreq['Message'])
            if identios != '' and ispush:
                iosmsg = {"appname": appname, "type": msgtype, "Message": info, "Summary": title,
                          "Target": "device", "TargetValue": identios}
                iosreq = requests.post(baseurl + '/push.ios', data=iosmsg).json()
                issave = iosreq['success']
                if iosreq['success']:
                    print 'IOS消息个推推送成功！'
                else:
                    print 'IOS消息个推推送失败！原因' + str(iosreq['Message'])
        # notice是通知
        else:

            if identandroid != '' and ispush:
                androidmsg = {"appname": appname, "type": msgtype, "Title": title, "Summary": info,
                              "Target": "device", "TargetValue": identandroid, "ext": ext}
                androidreq = requests.post(baseurl + '/push.android', data=androidmsg).json()
                issave = androidreq['success']
                if androidreq['success']:
                    print '安卓通知个推推送成功！'
                else:
                    print '安卓通知个推推送失败！原因' + str(androidreq['Message'])
            # print identios != '' and ispush
            if identios != '' and ispush:
                iosmsg = {"appname": appname, "type": msgtype, "Summary": title, "Target": "device",
                          "TargetValue": identios, "ext": ext}
                iosreq = requests.post(baseurl + '/push.ios', data=iosmsg).json()
                issave = iosreq['success']
                if iosreq['success']:
                    print 'IOS通知个推推送成功！'
                else:
                    print 'IOS通知个推推送失败！原因' + str(iosreq['Message'])
    elif target == 'all':
        if msgtype == 'message':
            if ispush:
                androidmsg = {"appname": appname, "type": msgtype, "Message": info, "Target": "all",
                              "TargetValue": "all"}
                androidreq = requests.post(baseurl + '/push.android', data=androidmsg).json()
                issave = androidreq['success']
                if androidreq['success']:
                    print '安卓消息全推推送成功！'
                else:
                    print '安卓消息全推推送失败！原因' + str(androidreq['Message'])
                iosmsg = {"appname": appname, "type": msgtype, "Message": info, "Summary": title, "Target": "all",
                          "TargetValue": "all"}
                iosreq = requests.post(baseurl + '/push.ios', data=iosmsg).json()
                issave = iosreq['success']
                if iosreq['success']:
                    print 'IOS消息全推推送成功！'
                else:
                    print 'IOS消息全推推送失败！原因' + str(iosreq['Message'])
        else:
            if ispush:
                androidmsg = {"appname": appname, "type": msgtype, "Title": title, "Summary": info, "Target": "all",
                              "TargetValue": "all", "ext": ext}
                androidreq = requests.post(baseurl + '/push.android', data=androidmsg).json()
                issave = androidreq['success']
                if androidreq['success']:
                    print '安卓通知全推推送成功！'
                else:
                    print '安卓通知全推推送失败！原因' + str(androidreq['Message'])
                iosmsg = {"appname": appname, "type": msgtype, "Summary": title, "Target": "all",
                          "TargetValue": "all", "ext": ext}
                iosreq = requests.post(baseurl + '/push.ios', data=iosmsg).json()
                issave = iosreq['success']
                if iosreq['success']:
                    print 'IOS通知全推推送成功！'
                else:
                    print 'IOS通知全推推送失败！原因' + str(iosreq['Message'])
    else:
        pass
    mongo.message.update_one({"_id": str(mes)}, {"$set": {"androidmsg": androidmsg, "iosmsg": iosmsg}})
    return True
    #     return True
    # else:
    #     return False
    # except:
    #     return False


# 订座点菜提前一小时发给商家
def send56():
    pass
    item = mongo.order.find({"preset_time": {"$gte": datetime.datetime.now(),
                                             '$lt': datetime.datetime.now() + datetime.timedelta(hours=1)}})

    # mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
    # appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
    for i in item:
        print '111'
        # if i['webuser_id'] != '' and checkmsg(str(i['_id']),'5'):
        rname = getroom(str(i['restaurant_id']), i['room_id'])
        tuisong(mfrom='',
                mto=str(i['restaurant_id']),
                title='订单提醒',
                info=rname + '在' + i['preset_time'].strftime('%Y年%m月%d日 %H:%M:%S') + '有预定',
                goto='5',
                channel='订单提醒',
                type='0',
                totype='0',
                appname='foodmap_shop',
                msgtype='notice',
                target='device',
                ext='{"goto":"5","id":"' + str(i['_id']) + '"}',
                ispush=True,
                data_id=str(i['_id']))
    print 'send56:订座点菜提前一小时发给商家'


# 优惠/活动过期/被抢光 一天
def send7():
    pass
    # mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
    # appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
    coupons = mongo.coupons.find({"num": 0})
    for i in coupons:
        if checkmsg(str(i['_id']), '7'):
            tuisong(mfrom=str(i['webuser_id']),
                    mto=str(i['rstaurant_id']),
                    title='您发布的优惠被...',
                    info='您发布的优惠被抢光了，快去发布新的优惠吧',
                    goto='7',
                    channel='优惠提醒',
                    type='0',
                    totype='0',
                    appname='foodmap_shop',
                    msgtype='notice',
                    target='device',
                    ext='',
                    ispush=False,
                    data_id=str(i['_id']))
    coupons2 = mongo.coupons.find({"showtime_end": {"$gte": datetime.datetime.now()}})
    for c in coupons2:
        if checkmsg(str(c['_id']), '7'):
            tuisong(mfrom=str(c['webuser_id']),
                    mto=str(c['rstaurant_id']),
                    title='您发布的优惠过...',
                    info='您发布的优惠过期了，快去发布新的优惠吧',
                    goto='7',
                    channel='优惠提醒',
                    type='0',
                    totype='0',
                    appname='foodmap_shop',
                    msgtype='notice',
                    target='device',
                    ext='',
                    ispush=False,
                    data_id=str(c['_id']))
    kaituan = mongo.order_groupinvite.find({"time2": {"$gte": datetime.datetime.now()}})
    for k in kaituan:
        if checkmsg(str(k['_id']), '7'):
            tuisong(mfrom='',
                    mto=str(k['rstaurant_id']),
                    title='您发布的活动过...',
                    info='您发布的活动过期了，快去发布新的活动吧',
                    goto='7',
                    channel='活动提醒',
                    type='0',
                    totype='0',
                    appname='foodmap_shop',
                    msgtype='notice',
                    target='device',
                    ext='',
                    ispush=False,
                    data_id=str(k['_id']))
    kaituan2 = mongo.order_groupinvite.find({})
    from app_user.groupinvite import GroupInvite
    for k2 in kaituan2:
        if checkmsg(str(k2['_id']), '7') and GroupInvite()._is_invite_open(str(k2['_id'])) < 1:
            tuisong(mfrom='',
                    mto=str(k['rstaurant_id']),
                    title='您发布的活动被...',
                    info='您发布的活动被抢光了，快去发布新的活动吧',
                    goto='7',
                    channel='活动提醒',
                    type='0',
                    totype='0',
                    appname='foodmap_shop',
                    msgtype='notice',
                    target='device',
                    ext='',
                    ispush=False,
                    data_id=str(k['_id']))
    print 'send7:优惠/活动过期/被抢光 一天'


# 开团请客失败
def send10():
    # mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
    # appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
    kaituan = mongo.order_groupinvite.find({"status": {"$in": ["timeout", "else"]}})
    for i in kaituan:
        if checkmsg(str(i['_id']), '10'):
            tuisong(mfrom='',
                    mto=str(i['restaurant_info']['rid']),
                    title=i['restaurant_info']['name'],
                    info='您的' + i['restaurant_info']['name'] + '开团请客失败了',
                    goto='10',
                    channel='请客提醒',
                    type='0',
                    totype='1',
                    appname='foodmap_user',
                    msgtype='notice',
                    target='device',
                    ext='{"goto":"10","id":"' + str(i['_id']) + '"}',
                    ispush=True,
                    data_id=str(i['_id']))
    print 'send10:开团请客失败'


# 开团请客就餐提醒 一天
def send14():
    kaituan = mongo.order_groupinvite.find(
        {"end_time": {'$lt': datetime.datetime.now() + datetime.timedelta(hours=24)}})
    for i in kaituan:
        if checkmsg(str(i['_id']), '14'):
            tuisong(mfrom='',
                    mto=str(i['master_id']),
                    title=i['restaurant_info']['name'],
                    info='您的' + i['restaurant_info']['name'] + '请客活动要开餐了',
                    goto='14',
                    channel='请客提醒',
                    type='0',
                    totype='1',
                    appname='foodmap_user',
                    msgtype='notice',
                    target='device',
                    ext='{"goto":"14","id":"' + str(i['_id']) + '"}',
                    ispush=True,
                    data_id=str(i['_id']))
    print 'send14:开团请客就餐提醒 一天'


# 优惠到期提醒 一天
def send15():
    kaituan = mongo.mycoupons.find({"indate_end": {'$lt': datetime.datetime.now() + datetime.timedelta(hours=24)}})
    for i in kaituan:
        if checkmsg(str(i['_id']), '15'):
            tuisong(mfrom='',
                    mto=str(i['webuser_id']),
                    title='您的优惠快到期了',
                    info='店铺名称：' + i['r_name'] + '，优惠：' + i['content'] + '，有效期：' + i['expiry_date'],
                    goto='15',
                    channel='优惠提醒',
                    type='0',
                    totype='1',
                    appname='foodmap_user',
                    msgtype='notice',
                    target='device',
                    ext='',
                    ispush=False,
                    data_id=str(i['_id']))
    print 'send15:优惠到期提醒 一天'


# 未按时支付 订单自动取消
def send16():
    order = mongo.order.find({"status": 6})
    for i in order:
        if checkmsg(str(i['_id']), '16'):
            tuisong(mfrom='',
                    mto=str(i['webuser_id']),
                    title='您的订单已被取消',
                    info='快去看看吧！',
                    goto='16',
                    channel='订单提醒',
                    type='0',
                    totype='1',
                    appname='foodmap_user',
                    msgtype='notice',
                    target='device',
                    ext='{"goto":"16","id":"' + str(i['_id']) + '"}',
                    ispush=True,
                    data_id=str(i['_id']))
    print 'send16:未按时支付 订单自动取消'


def my_listener(event):
    if event.exception:
        print '任务出错了！！！！！！'
    else:
        print '任务照常运行...'


# scheduler = BlockingScheduler()
# # scheduler.add_job(func=date_test, args=('一定性任务,会出错',), trigger='interval',seconds=3, id='date_task')
# # scheduler.add_job(func=aps_test, args=('循环任务',1), trigger='interval', seconds=3, id='interval_task')
# scheduler.add_job(func=send56,trigger='interval', seconds=3600,id='interval_task1')
# scheduler.add_job(func=send7,trigger='interval', seconds=86400,id='interval_task2')
# scheduler.add_job(func=send10,trigger='interval', seconds=60,id='interval_task3')
# scheduler.add_job(func=send14,trigger='interval', seconds=86400,id='interval_task4')
# scheduler.add_job(func=send15,trigger='interval', seconds=86400,id='interval_task5')
# scheduler.add_job(func=send16,trigger='interval', seconds=60,id='interval_task6')
# scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
# scheduler._logger = logging

# scheduler.start()
if __name__ == '__main__':
    send56()

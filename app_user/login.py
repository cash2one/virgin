# coding=utf-8
import hashlib
from connect.mongotool import MongoAPI
import requests
import random
from flasgger import swag_from
from app_merchant import auto
import sys
from tools.db_app_user import guess
from tools.swagger import swagger
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Blueprint,abort,request,json
from connect import conn,settings
from bson import ObjectId,json_util
import tools.tools as tool
import datetime


login_user_api = Blueprint('login_user_api', __name__, template_folder='templates')
mongouser = conn.mongo_conn_user()
mongo = MongoAPI(conn.mongo_conn_user().user_web)
SMSnetgate = settings.SMSnetgate
# SMSnetgate = 'http://127.0.0.1:10032'
#发送验证码
send_sms = swagger("0-1 注册.jpg","发送验证码")
send_sms.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
send_sms.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话号码',default='13000000000')

send_sms_json = {
    "auto": send_sms.String(description='验证是否成功'),
    "message": send_sms.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": send_sms.Integer(description='',default=0),
    "data": {
            "ispass":send_sms.Boolean(description='是否发送成功',default=True),
    }
}

#发送验证码
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/send_sms/',methods=['POST'])
@swag_from(send_sms.mylpath(schemaid='send_sms',result=send_sms_json))
def send_sms():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                # if mongo.find({"phone":request.form['phone']}):
                data = {'sign': '美食地图',
                        'tpl': 'SMS_8161119',
                        'param': json.dumps({"code": str(random.randint(1000000, 9999999))[1:]}),
                        'tel': request.form['phone'],
                        'ex': '#foodmap.mobile'
                        }
                req = requests.post(SMSnetgate + '/sms.send', data)
                result=tool.return_json(0,"success",True,{"ispass":req.json()['success']})
                # else:
                #     result=tool.return_json(0,"field",True,{"ispass":False,"message":"请先注册"})
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
send_sms2 = swagger("0-1 注册.jpg","发送验证码2：加判断")
send_sms2.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
send_sms2.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话号码',default='13000000000')
send_sms2.add_parameter(name='flag',parametertype='formData',type='string',required= True,description='登陆传user_login，注册传user_register',default='user_register')

send_sms2_json = {
    "auto": send_sms2.String(description='验证是否成功'),
    "message": send_sms2.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": send_sms2.Integer(description='',default=0),
    "data": {
            "ispass":send_sms2.Boolean(description='是否发送成功',default=True),
    }
}

#发送验证码2
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/send_sms2/',methods=['POST'])
@swag_from(send_sms2.mylpath(schemaid='send_sms2',result=send_sms2_json))
def send_sms2():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                flag = request.form['flag']
                if flag == 'user_login':
                    if mongo.find({"phone":request.form['phone'],"appid.2":True}):
                        data = {'sign': '美食地图',
                                'tpl': 'SMS_8161119',
                                'param': json.dumps({"code": str(random.randint(1000000, 9999999))[1:]}),
                                'tel': request.form['phone'],
                                'ex': '#foodmap.mobile'
                                }
                        req = requests.post(SMSnetgate + '/sms.send', data)
                        result=tool.return_json(0,"success",True,{"ispass":req.json()['success']})
                    else:
                        result=tool.return_json(0,"field",True,{"ispass":False,"message":"请先注册"})
                    pass
                elif flag == 'user_register':
                    if mongo.find({"phone":request.form['phone'],"appid.2":True}):
                        result=tool.return_json(0,"field",True,{"ispass":False,"message":"已注册，请登录"})
                    else:
                        data = {'sign': '美食地图',
                                'tpl': 'SMS_8161119',
                                'param': json.dumps({"code": str(random.randint(1000000, 9999999))[1:]}),
                                'tel': request.form['phone'],
                                'ex': '#foodmap.mobile'
                                }
                        req = requests.post(SMSnetgate + '/sms.send', data)
                        result=tool.return_json(0,"success",True,{"ispass":req.json()['success'],"message":"成功"})

                else:
                    result=tool.return_json(0,"field",True,{"ispass":False,"message":"请使用正确的type"})
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
#注册
register = swagger("0-1 注册.jpg","注册")
register.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
register.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话',default='13000000000')
register.add_parameter(name='password',parametertype='formData',type='string',required= True,description='密码',default='111111')
register.add_parameter(name='code',parametertype='formData',type='string',required= True,description='六位验证码',default='000000')
register_json = {
    "auto": register.String(description='验证是否成功'),
    "message": register.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": register.Integer(description='',default=0),
    "data": {
        "_id": register.String(description='用户id',default="57bbbe6ffb98a40c6431b28f"),
        "ispass": register.Boolean(description='是否注册成功',default=True),
        "info": register.String(description='返回信息',default="成功或者失败"),
    }
}

#注册
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/register/',methods=['POST'])
@swag_from(register.mylpath(schemaid='register',result=register_json))
def register():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                phone = request.form['phone']
                password = request.form['password']
                code = request.form['code']
                data = {'tel': phone,
                'ex': '#foodmap.mobile',
                'tpl': 'SMS_8161119',
                'code': code}
                req = requests.post(SMSnetgate + '/sms.validate', data)
                if req.json()['success']:
                    data = {
                        "status": 1,
                        "identification": "",
                        "registeruser": {
                            "nick": "",
                            "password": hashlib.md5(password).hexdigest().upper(),
                            "headimage": "",
                            "name": ""
                        },
                        "lastlogin": {
                            "ident": "",
                            "type":"",
                            "time": datetime.datetime.now()
                        },
                        "thirdIds": [
                        ],
                        "phone": phone,
                        "addtime": datetime.datetime.now(),
                        "type": 3,
                        "identype": "0",
                        "appid": {'2': True}
                    }
                    # item = mongo.user_web.insert(json)
                    user_web = mongo.find({'phone': phone})
                    if not user_web:
                            item = mongo.add(data)
                            if item['success']:
                                from tools.tools import qrcode as qr
                                webuser_add = conn.mongo_conn().webuser.insert({"automembers_id": item['_id'],
                                                                                "nickname": phone,
                                                                                "gender": 1,
                                                                                "birthday": "",
                                                                                "headimage": "",
                                                                                "phone": phone})
                                webuser_add = json_util.loads(json_util.dumps(webuser_add))
                                print webuser_add
                                user_addqr = conn.mongo_conn().webuser.update({'_id': ObjectId(webuser_add)},
                                                                              {'$set': {'qrcode_img': qr(json.dumps({
                                                                                  'fuc': 'webuser',
                                                                                  'info': {
                                                                                      'user_id': str(webuser_add)
                                                                                  }
                                                                              }))}})
                                user_addqr = json_util.loads(json_util.dumps(user_addqr))
                                result=tool.return_json(0,"success",True,{'ispass':True,'_id': str(webuser_add),'info': '注册成功'})
                                return json_util.dumps(result,ensure_ascii=False,indent=2)
                            else:
                                result=tool.return_json(0,"success",True,{'ispass':False,'_id': '','info': '注册失败'})
                                return json_util.dumps(result,ensure_ascii=False,indent=2)
                    elif  '2' not in user_web[0]['appid']:
                        #非用户
                        # print user_web
                        # print user_web[0]["_id"]
                        # print user_web[0]["_id"]["$oid"]
                        # mongo.fix({
                        #     "_id":user_web[0]["_id"]["$oid"],
                        #     "appid":{"1":True,"2":True}
                        # })
                        userweb = mongo.conn.update_one({"_id":ObjectId(user_web[0]["_id"]["$oid"])},{"$set":{"appid":{"1":True,"2":True},                        "registeruser": {
                            "nick": "",
                            "password": hashlib.md5(password).hexdigest().upper(),
                            "headimage": "",
                            "name": ""
                        },}})
                        from tools.tools import qrcode as qr
                        webuser_add = conn.mongo_conn().webuser.insert({"automembers_id": user_web[0]["_id"]["$oid"],
                                                                        "nickname": phone,
                                                                        "gender": 1,
                                                                        "birthday": "",
                                                                        "headimage": "",
                                                                        "qrcode_img":"",
                                                                        "phone": phone})
                        webuser_add = json_util.loads(json_util.dumps(webuser_add))
                        print webuser_add
                        user_addqr = conn.mongo_conn().webuser.update({'_id': ObjectId(webuser_add)},
                                                                      {'$set': {'qrcode_img': qr(json.dumps({
                                                                          'fuc': 'webuser',
                                                                          'info': {
                                                                              'user_id': str(webuser_add)
                                                                          }
                                                                      }))}})
                        user_addqr = json_util.loads(json_util.dumps(user_addqr))
                        result=tool.return_json(0,"success",True,{'ispass':True,'_id': str(user_web[0]["_id"]["$oid"]),'info': '注册成功'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                    else:
                        result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '此账号已注册'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '验证码超时或错误，请重新输入'})
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",True,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#密码登录
verify_login = swagger("0-3 登录.jpg","密码登录")
verify_login.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
verify_login.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话',default='13000000000')
verify_login.add_parameter(name='password',parametertype='formData',type='string',required= True,description='密码',default='111111')
verify_login.add_parameter(name='ident',parametertype='formData',type='string',required= True,description='设备号',default='')
verify_login.add_parameter(name='phonetype',parametertype='formData',type='string',required= True,description='手机类型 安卓0 IOS1',default='')

verify_login_json = {
    "auto": verify_login.String(description='验证是否成功'),
    "message": verify_login.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": verify_login.Integer(description='',default=0),
    "data": {
        "_id": verify_login.String(description='用户id',default="57bbbe6ffb98a40c6431b28f"),
        "ispass": verify_login.Boolean(description='是否登陆成功',default=True),
        "info": verify_login.String(description='返回信息',default="成功或者失败"),
    }
}

#密码登录
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/verify_login/',methods=['POST'])
@swag_from(verify_login.mylpath(schemaid='verify_login',result=verify_login_json))
def verify_login():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                phone = request.form['phone']
                password = request.form['password']
                ident = request.form['ident']
                flag = False
                if "phonetype" in request.form:
                    phonetype = request.form['phonetype']
                    flag = True
                else:
                    phonetype = ''
                    pass
                found = mongo.find({'phone': phone, 'appid.2': True})
                print found
                if found and flag:
                    print '1111111111111111111111111111'
                    # data = {
                    #     "lastlogin": {
                    #             "ident": ident,
                    #             "type":phonetype,
                    #             "time": datetime.datetime.now()
                    #         }
                    # }
                    # conn.mongo_conn().user_web.update({"_id":found[0]['_id']},{"$set":data})
                    mongo.fix({
                        "_id":found[0]['_id']['$oid'],
                        "fix_data":{
                            "lastlogin": {
                                "ident": ident,
                                "type":phonetype,
                                "time": datetime.datetime.now()
                            }
                        }
                    })
                    found = found[0]
                    if found['registeruser']['password'] == hashlib.md5(password).hexdigest().upper():
                        found['_id'] = str(found['_id']['$oid'])
                        user = conn.mongo_conn().webuser.find({"automembers_id":found['_id']})
                        user_id = ''
                        for u in user:
                            user_id = str(u['_id'])
                        result=tool.return_json(0,"success",True,{'ispass':True,'_id': user_id,'info': '密码登陆成功'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                    else:
                        result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '密码错误'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '没有此账号'})
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",True,str(e))
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#验证码登录
code_login = swagger("0-2 快捷登录.jpg","验证码登录")
code_login.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
code_login.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话',default='13000000000')
code_login.add_parameter(name='code',parametertype='formData',type='string',required= True,description='六位验证码',default='000000')
code_login.add_parameter(name='ident',parametertype='formData',type='string',required= True,description='设备号',default='')
code_login.add_parameter(name='phonetype',parametertype='formData',type='string',required= True,description='手机类型 安卓0 IOS1',default='')
code_login_json = {
    "auto": code_login.String(description='验证是否成功'),
    "message": code_login.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": code_login.Integer(description='',default=0),
    "data": {
        "_id": code_login.String(description='用户id',default="57bbbe6ffb98a40c6431b28f"),
        "ispass": code_login.Boolean(description='是否登陆成功',default=True),
        "info": code_login.String(description='返回信息',default="成功或者失败"),
    }
}

#验证码登录
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/code_login/',methods=['POST'])
@swag_from(code_login.mylpath(schemaid='code_login',result=code_login_json))
def code_login():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                phone = request.form['phone']
                code = request.form['code']
                flag = False
                if "phonetype" in request.form:
                    phonetype = request.form['phonetype']
                    flag = True
                else:
                    phonetype = ''
                    pass
                found = mongo.find({'phone': phone, 'appid.2': True})
                if found and flag:
                    mongo.fix({
                        "_id":found[0]['_id']['$oid'],
                        "fix_data":{
                            "lastlogin": {
                                "ident": request.form['ident'],
                                "type":phonetype,
                                "time": datetime.datetime.now()
                            }
                        }
                    })
                    found = found[0]
                    data = {'tel': phone,
                        'ex': '#foodmap.mobile',
                        'tpl': 'SMS_8161119',
                        'code': code}
                    req = requests.post(SMSnetgate + '/sms.validate', data)
                    if req.json()['success']:
                        found['_id'] = str(found['_id']['$oid'])
                        user = conn.mongo_conn().webuser.find({"automembers_id":found['_id']})
                        user_id = ''
                        for u in user:
                            user_id = str(u['_id'])
                        result=tool.return_json(0,"success",True,{'ispass':True,'_id': user_id,'info': '验证码登陆成功'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                    else:
                        result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '验证码超时或错误，请重新输入'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '没有此账号'})
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
                pass
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#找回密码
resetpassword = swagger("0-4 找回密码.jpg","找回密码")
resetpassword.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
resetpassword.add_parameter(name='phone',parametertype='formData',type='string',required= True,description='电话',default='13000000000')
resetpassword.add_parameter(name='password',parametertype='formData',type='string',required= True,description='密码',default='111111')
resetpassword.add_parameter(name='code',parametertype='formData',type='string',required= True,description='六位验证码',default='000000')

resetpassword_json = {
    "auto": resetpassword.String(description='验证是否成功'),
    "message": resetpassword.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": resetpassword.Integer(description='',default=0),
    "data": {
        "_id": resetpassword.String(description='用户id',default="57bbbe6ffb98a40c6431b28f"),
        "ispass": resetpassword.Boolean(description='是否修改密码成功',default=True),
        "info": resetpassword.String(description='返回信息',default="成功或者失败"),
    }
}

#找回密码
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/resetpassword/',methods=['POST'])
@swag_from(resetpassword.mylpath(schemaid='resetpassword',result=resetpassword_json))
def resetpassword():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                phone = request.form['phone']
                code = request.form['code']
                password = request.form['password']
                data = {'tel': phone,
                        'ex': '#foodmap.mobile',
                        'tpl': 'SMS_8161119',
                        'code': code}
                req = requests.post(SMSnetgate + '/sms.validate', data)
                if req.json()['success']:
                    found = mongo.find({'phone': phone, 'appid.2':True})
                    if found:
                        found = found[0]
                        fix_psw = {'registeruser.password': hashlib.md5(password).hexdigest().upper()}
                        is_fix = mongo.fix({'_id': str(found['_id']['$oid']), 'fix_data': fix_psw})
                        is_fix['_id'] = str(found['_id']['$oid'])
                        result=tool.return_json(0,"success",True,{'ispass':True,'_id': is_fix['_id'],'info': '找回密码成功'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                        pass
                    else:
                        result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '没有此账号'})
                        return json_util.dumps(result,ensure_ascii=False,indent=2)
                else:
                    result=tool.return_json(0,"success",True,{'ispass':False,'_id':'','info': '验证码超时或错误，请重新输入'})
                    return json_util.dumps(result,ensure_ascii=False,indent=2)
                pass
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,str(e))
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
checkphonetype = swagger("其他","改用户中心lastlogin最后登录type 用来修改BUG数据")
checkphonetype.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
checkphonetype.add_parameter(name='phonetype',parametertype='formData',type='string',required= True,description='设备类型：安卓传0，IOS传1',default='0')
checkphonetype.add_parameter(name='user_id',parametertype='formData',type='string',required= True,description='用户id',default='')

checkphonetype_json = {
    "auto": checkphonetype.String(description='验证是否成功'),
    "message": checkphonetype.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": checkphonetype.Integer(description='',default=0),
    "data": checkphonetype.String(description='修改成功',default="无需修改"),
}

#改最后登录type 用来修改数据
@login_user_api.route(settings.app_user_url+'/fm/user/v1/login/checkphonetype/',methods=['POST'])
@swag_from(checkphonetype.mylpath(schemaid='checkphonetype',result=checkphonetype_json))
def checkphonetype():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                user_id = request.form['user_id']
                user = conn.mongo_conn().webuser.find({"_id":ObjectId(user_id)})
                u_id = ''
                for u in user:
                    u_id = u['automembers_id']
                phonetype = request.form['phonetype']
                msg = ""
                item = mongouser.user_web.find({"_id":ObjectId(u_id)})
                for i in item:
                    if "type" not in i['lastlogin'].keys():
                        mongouser.user_web.update_one({"_id":ObjectId(u_id)},{"$set":{"lastlogin.type":phonetype}})
                        msg = "修改成功"
                    else:
                        msg = "无需修改"
                        pass
                result=tool.return_json(0,"success",True,msg)
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
    # print send_sms()
    # print sms_validate()
    # print register()
    # print verify_login()
    # print code_login()
    # print resetpassword()
    found = mongo.find({'phone': '15636322331', 'appid.2': True})
    print json_util.dumps(found,ensure_ascii=False,indent=2)
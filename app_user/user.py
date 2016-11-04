# coding=utf-8
from flask import Blueprint, render_template, request, abort, json
from connect import conn
from connect.mongotool import MongoAPI
import tools.tools as tool
from bson import json_util, ObjectId
import pymongo
import datetime
import hashlib

__author__ = 'hcy'

user_api = Blueprint("user_api", __name__, template_folder='templates')
# mongo = conn.mongo_conn_user()
mongo = MongoAPI(conn.mongo_conn_user().user_web)


@user_api.route('/usercenter/v1/register/', methods=['POST'])
def register():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]

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
        if not mongo.find({'phone': phone, 'appid': {'2': True}}):
            item = mongo.add(data)
            if item['success']:
                from tools.tools import qrcode as qr
                webuser_add = conn.mongo_conn().webuser.insert({"automembers_id": item['_id'],
                                                                "nickname": request.form["nickname"],
                                                                "gender": 1,
                                                                "birthday": "",
                                                                "headimage": "",
                                                                "phone": request.form["phone"]})
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
                return json_util.dumps({'success': True, '_id': str(webuser_add)})
            else:
                return json_util.dumps(item.update({'success': False}))
        else:
            return json_util.dumps({'success': False, 'info': 'Database already had one'})
            # print str(item)
            # r = {"id": str(item)}
            # return json_util.dumps(item, ensure_ascii=False, indent=2)
    else:
        return abort(403)


@user_api.route('/usercenter/v1/login/', methods=['POST'])
def verify_login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        flag = False
        if "phonetype" in request.form:
            phonetype = request.form['phonetype']
            flag = True
        else:
            phonetype = ''
            pass
        found = mongo.find({'phone': phone, 'appid': {'2': True}})
        if 'seller' in request.form:
            print 'is seller'
        if found:
            found = found[0]
            if found['registeruser']['password'] == hashlib.md5(password).hexdigest().upper():
                found['_id'] = str(found['_id']['$oid'])
                if flag:
                    data = {
                        "_id":str(found['_id']['$oid']),
                        "fix_data":{
                            "lastlogin" :{
                                "ident": "",
                                "type":phonetype,
                                "time": datetime.datetime.now()
                            }
                        }
                    }
                    mongo.fix(data)
                return json.dumps({'success': True, '_id': found['_id']})
            else:
                return json.dumps({'success': False, 'info': 'Password Not Match'})
        else:
            return json.dumps({'success': False, 'info': 'Not Found'})
        pass
    else:
        return abort(403)
    pass


@user_api.route('/usercenter/v1/isuser', methods=['POST'])
def is_user():
    if request.method == "POST":
        phone = request.form['phone']
        found = mongo.find({'phone': phone, 'appid': {'2': True}})
        if found:
            found = found[0]
            return json.dumps({'success': True, '_id': str(found['_id'])})
        else:
            return json.dumps({'success': False, 'info': 'Not Found'})
    else:
        return abort(403)
    pass


@user_api.route('/usercenter/v1/reset/', methods=['POST', 'PATCH'])
def password_reset():
    if request.method in ['POST', 'PATCH']:
        phone = request.form["phone"]
        password = request.form["password"]
        found = mongo.find({'phone': phone, 'appid': {'2': True}})
        if found:
            found = found[0]
            fix_psw = {'registeruser.password': hashlib.md5(password).hexdigest().upper()}
            is_fix = mongo.fix({'_id': str(found['_id']['$oid']), 'fix_data': fix_psw})
            is_fix['_id'] = str(found['_id']['$oid'])
            return json.dumps(is_fix)
            pass
        else:
            return json.dumps({'success': False, 'info': 'Not Found'})
        pass
    else:
        pass
    pass


@user_api.route('/admin/v1/login/', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        from tools.user_infos import GetUser
        req = GetUser({'phone': request.form['phone'],
                       'ident': request.form['ident'],
                       'ex': '#foodmap.mobile',
                       'tpl': 'SMS_8161119',
                       'code': request.form['code'] if 'code' in request.form else ''})
        if request.form['method'] == 'send_sms':
            if req.is_admin:
                try:
                    req.send_sms()
                    return json.dumps({'success': True})
                except Exception, e:
                    print e
                    return json.dumps({'success': False})
            else:
                return json.dumps({'success': False, 'info': 'Not admin'})
        elif request.form['method'] == 'shop_id':
            if req.is_admin:
                # print req.admin_shop_id
                data = {
                    "_id":str(req.user_center_id),
                    "fix_data":{
                        "lastlogin" :{
                            "ident": "",
                            # "type": request.form.get('phonetype', ''),
                            "type":request.form['phonetype'] if "phonetype" in request.form else "",
                            "time": datetime.datetime.now()
                        }
                    }
                }
                mongo.fix(data)
                return json.dumps(req.admin_shop_id)
            else:
                return json.dumps({'success': False, 'info': 'Not admin'})
        else:
            return json.dumps({'success': False, 'info': 'method inputError'})
    else:
        return abort(403)
    pass


class Test:
    @staticmethod
    def find_user():
        test = mongo.find({'phone': '19782349087190'})
        print str(test[0]['_id']['$oid'])
        print json_util.dumps(test, indent=2)

    @staticmethod
    def login():
        phone = '18504513506'
        password = '123'
        found = mongo.find({'phone': phone, 'appid': 2})
        if found:
            found = found[0]
        if found:
            print hashlib.md5(password).hexdigest().upper()
            if found['registeruser']['password'] == hashlib.md5(password).hexdigest().upper():
                found['_id'] = str(found['_id']['$oid'])
                print found['registeruser']['password']
                print json.dumps({'success': True, 'info': found})
            else:
                print json.dumps({'success': False, 'info': 'Password Not Match'})
        else:
            print json.dumps({'success': False, 'info': 'Not Found'})

    @staticmethod
    def fix_password():
        password = '123'
        fix_psw = {'registeruser.password': hashlib.md5(password).hexdigest().upper()}
        print fix_psw
        is_fix = mongo.fix({'_id': '573e5c00dcc88e6873eab9ad', 'fix_data': fix_psw})
        print is_fix
        pass

    @staticmethod
    def add_user():
        phone = '123134134'
        password = 'asdfasdf'
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
        item = mongo.add(data)
        print item


if __name__ == '__main__':
    # Test.login()
    # Test.add_user()
    pass

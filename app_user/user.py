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

user_api = Blueprint("user_api", __name__, template_folder='templates',url_prefix='')
# user_api = Blueprint("user_api", __name__, template_folder='templates',url_prefix='/fm/merchant')
# mongo = conn.mongo_conn_user()
mongo = MongoAPI(conn.mongo_conn_user().user_web)




@user_api.route('/usercenter/v1/register/', methods=['POST'])
def register():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        user_data = mongo.find({'phone': phone})

        if user_data:   # 判断是否存在用户数据
            data = user_data[0]
            user_id = str(user_data[0]['_id']['$oid'])
            if '2' in data['appid']:  # 如果已经注册
                return json_util.dumps({'success': False, 'info': 'Database already had one'})
            else:   # 如果未注册用户版
                data['registeruser'] = dict(
                    nick='',
                    password=hashlib.md5(password).hexdigest().upper(),
                    headimage='',
                    name=''
                )
                data['appid']['2']=True
            print data
            data['addtime'] = datetime.datetime.now()
            data['lastlogin']['time'] = datetime.datetime.now()
            del data['_id']
            data = dict(fix_data=data, _id=user_id)
            # data['_id'] = user_id

            item = mongo.fix(data)
            item['_id'] = user_id
        else:   # 不存在用户数据
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
                    "type": "",
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
        found = mongo.find({'phone': phone, 'appid.2': True})
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
        found = mongo.find({'phone': phone, 'appid.2': True})
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
        found = mongo.find({'phone': phone, 'appid.2': True})
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

def make_sure_sms_send(phone, ident):
    tpl_list = ['8161119', '7945138', '16040003', '16035004']
    result = None
    from tools.user_infos import GetUser
    for tpl in tpl_list:
        req = GetUser({'phone': phone,
                       'ident': ident,
                       'ex': '#foodmap.mobile',
                       'tpl': 'SMS_'+tpl,
                       'code': ''})
        result = req.send_sms('SMS_'+tpl)['callback']
        if 'result' in result:
            result['success'] = True
            return result
    result['success'] = False
    return result
    pass
@user_api.route('/admin/v1/login/', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        from tools.user_infos import GetUser
        req = GetUser({'phone': request.form['phone'],
                       'ident': request.form['ident'],
                       'ex': '#foodmap.mobile',
                       'tpl': 'SMS_8161119',
                       'code': request.form['code'] if 'code' in request.form else '',
                       'phonetype':request.form.get('phonetype','')})
        if request.form['method'] == 'send_sms':
            if req.is_admin:
                send = make_sure_sms_send(request.form['phone'], request.form['ident'])
                return json.dumps(send)
            else:
                return json.dumps({'success': False, 'info': 'Not admin'})
        elif request.form['method'] == 'shop_id':
            if req.is_admin:
                # print req.admin_shop_id
                data = {
                    "_id":str(req.user_center_id),
                    "fix_data":{
                        "lastlogin" :{
                            "ident": request.form['ident'],
                            # "type": request.form.get('phonetype', ''),
                            "type":request.form.get('phonetype',''),
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


if __name__ == '__main__':
    # Test.login()
    # Test.add_user()
    pass

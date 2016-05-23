from flask import Blueprint, render_template, request, abort, json
from connect import conn
import tools.tools as tool
from bson import json_util, ObjectId
import pymongo
import datetime
import hashlib

__author__ = 'hcy'

user_api = Blueprint("user_api", __name__, template_folder='templates')
# mongo = conn.mongo_conn_user()
mongo = conn.MongoAPI(conn.mongo_conn_user().user_web)


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
            return json_util.dumps(item)
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
        found = mongo.find({'phone': phone, 'appid': {'2': True}})[0]
        if found:
            if found['registeruser']['password'] == hashlib.md5(password).hexdigest().upper():
                found['_id'] = str(found['_id']['$oid'])
                return json.dumps({'success': True, '_id': found['_id']})
            else:
                return json.dumps({'success': False, 'info': 'Password Not Match'})
        else:
            return json.dumps({'success': False, 'info': 'Not Found'})
        pass
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
        phone = '15546226998'
        password = '123456'
        found = mongo.find({'phone': phone, 'appid': 1})[0]
        if found:
            print hashlib.md5(password).hexdigest().upper()
            if found['registeruser']['password'] == hashlib.md5(password).hexdigest().upper():
                found['_id'] = str(found['_id']['$oid'])
                print json.dumps({'success': True, 'info': found})
            else:
                print json.dumps({'success': False, 'info': 'Password Not Match'})
        else:
            print json.dumps({'success': False, 'info': 'Not Found'})


if __name__ == '__main__':
    pass

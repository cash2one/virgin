__author__ = 'hcy'
from flask import Blueprint,render_template,request
from connect import conn
import pymongo
import tools.tools as tool
from bson import  json_util
import datetime

user_api=Blueprint("user_api",__name__,template_folder='templates')
mongo=conn.mongo_conn_user()

@user_api.route('/usercenter/v1/register/', methods=['POST'])
def register():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]
        json = {
            "status" : 1,
            "identification" : "",
            "registeruser" : {
                "nick" : "",
                "password" : password,
                "headimage" : "",
                "name" : ""
            },
            "lastlogin" : {
                "ident" : "",
                "time" : datetime.datetime.now()
            },
            "thirdIds" : [
            ],
            "phone" : phone,
            "addtime" : datetime.datetime.now(),
            "type" : 3,
            "identype" : "0",
            "appid":2
        }
        item=mongo.user_web.insert(json)
    print str(item)
    r = {"id":str(item)}
    return json_util.dumps(r,ensure_ascii=False,indent=2)


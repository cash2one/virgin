__author__ = 'hcy'
import jwt
from bson import json_util
from connect import conn
from flask import Blueprint,jsonify,abort,render_template,request,json
import base64
import hashlib
import time
import datetime
import hashlib
import tools.tools as tool

mongo=conn.mongo_conn_user()

auto_api = Blueprint('auto_api', __name__, template_folder='templates')

@auto_api.route('/fm/merchant/v1/auto/', methods=['POST'])
def auto():
    baoming = request.form["baoming"]
    ident = request.form["ident"]
    type = request.form["type"]
    payload = {
        "baoming":baoming,
        "ident":ident,
        "type":type
    }
    msg = encodejwt(payload)
    decodejwt(msg)
    if decodejwt(msg):
        json = {
            "jwt":str(msg)
        }
        result=tool.return_json(0,"success",True,json)
    else:
        json = {
            "jwt":""
        }
        result=tool.return_json(0,"success",False,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)




def encodejwt(payload):
    secret = "b4e6a2808fbbc5d0f6451675e18fa37d"
    msg = jwt.encode(payload,secret,algorithm='HS256')
    return msg


def decodejwt(msg):
    # print msg
    # print type(msg)
    # print type(str(msg))
    # a = str(msg)
    # secret =str(time.time() % 600)+"secretmhj"
    secret = "b4e6a2808fbbc5d0f6451675e18fa37d"
    demsg= jwt.decode(msg, secret, algorithms=['HS256'])

    m2 = hashlib.md5()
    m2.update(demsg["baoming"]+demsg["ident"])
    md5str = m2.hexdigest()
    # print "baoming"
    # print demsg["baoming"]
    # print "ident"
    # print demsg["ident"]
    # print "md5"
    # print md5str
    if demsg["type"]=="1":
        identity = mongo.auto_user.find_one({"android_ident":md5str})
    else:
        identity = mongo.auto_user.find_one({"iphone_ident":md5str})
    if identity:
        json = True
    else:
        json = False
    # result=tool.return_json(0,"success",json)
    return  json


# @order_api.route('/auto/<string:user>')
# def auto():



@auto_api.route('/fm/merchant/v1/getmd5/', methods=['POST'])
def getmd5():
    baoming = request.form["baoming"]
    ident = request.form["ident"]

    m2 = hashlib.md5()
    m2.update(baoming.strip()+ident.strip())
    md5str = m2.hexdigest()

    json = {
        "md5":md5str
    }
    result=tool.return_json(0,"success",True,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)

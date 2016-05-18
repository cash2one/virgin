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

mongo=conn.mongo_conn()

auto_api = Blueprint('auto_api', __name__, template_folder='templates')

@auto_api.route('/fm/merchant/v1/auto/', methods=['POST'])
def auto():
    baoming = request.form["baoming"]
    ident = request.form["ident"]
    payload = {
        "baoming":baoming,
        "ident":ident
    }
    msg = encodejwt(payload)
    print type(msg)
    return  json_util.dumps(msg)


def encodejwt(payload):
    secret = "b4e6a2808fbbc5d0f6451675e18fa37d"
    msg = jwt.encode(payload,secret,algorithm='HS256')
    return json_util.dumps(msg)


def decodejwt(msg):
    print msg
    print type(msg)
    print type(str(msg))
    a = str(msg)
    # secret =str(time.time() % 600)+"secretmhj"
    secret = "b4e6a2808fbbc5d0f6451675e18fa37d"
    demsg= jwt.decode(msg, secret, algorithms=['HS256'])

    # for key in demsg:
    #    print key d[key]


    m2 = hashlib.md5()
    # m2.update(src)
    md5str = m2.hexdigest()
    print md5str
    identity = mongo.auto_user.find_one("")
    return  json_util.dumps(demsg)


# @order_api.route('/auto/<string:user>')
# def auto():








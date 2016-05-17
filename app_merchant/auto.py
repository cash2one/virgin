__author__ = 'hcy'
import jwt
from bson import json_util
from connect import conn
from flask import Blueprint,jsonify,abort,render_template,request,json
import base64
import hashlib
import time
import datetime

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
    secret = "b4e6a2808fbbc5d0f6451675e18fa37d"
    msg = jwt.encode(payload,secret,algorithm='HS256')
    print type(msg)
    return  json_util.dumps(msg)






def encodejwt():
    payload = {
        "user_id":"sdfsfs"
    }
    # secret =str(time.time() % 600)+"secretmhj"
    secret ="secretmhj"
    print secret
    msg = jwt.encode(payload, secret, algorithm='HS256')
    print type(msg)
    return json_util.dumps(msg)


def decodejwt(msg):
    print msg
    print type(msg)
    print type(str(msg))
    a = str(msg)
    # secret =str(time.time() % 600)+"secretmhj"
    secret ="secretmhj"
    demsg= jwt.decode(msg, secret, algorithms=['HS256'])
    return  json_util.dumps(demsg)


# @order_api.route('/auto/<string:user>')
# def auto():








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

order_api = Blueprint('order_api', __name__, template_folder='templates')

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








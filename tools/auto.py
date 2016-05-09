__author__ = 'hcy'
import jwt
import base64
import hashlib
import time
import datetime
from bson import json_util

def encodejwt():
    payload = {
        "user_id":"sdfsfs"
    }
    # secret =str(time.time() % 600)+"secretmhj"
    secret ="secretmhj"
    print secret
    msg = jwt.encode(payload, secret, algorithm='HS256')
    print type(msg)
    return msg


def decodejwt(msg):
    print msg
    print type(msg)
    print type(str(msg))
    a = str(msg)
    # secret =str(time.time() % 600)+"secretmhj"
    secret ="secretmhj"
    # msg ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNsaWVudDEifQ.eyJ1c2VyX2lkIjoic2Rmc2ZzIn0.7QhkauxwO6YKD3_oopD7z_bDViWUUU7C9Z-x2DdlLAE"
    demsg= jwt.decode(msg, secret, algorithms=['HS256'])
    # return json_util.dumps(demsg)
    return  demsg

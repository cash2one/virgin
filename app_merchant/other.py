#coding=utf-8
import connect

__author__ = 'hcy'
from flask import Blueprint,render_template,request
from connect import conn
import pymongo
import tools.tools as tool
from bson import  json_util
import auto
import os

from flask import request, Response
import sys
reload(sys)
sys.setdefaultencoding('utf8')
other_api=Blueprint("other_api",__name__,template_folder='templates')
mongo=conn.mongo_conn()

@other_api.route('/fm/merchant/v1/appversion/', methods=['POST'])
def appversion():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
    jwtmsg = auto.decodejwt(jwtstr)
    json={}
    if jwtmsg:
        item=mongo.android_version.find().sort("addtime",pymongo.DESCENDING)[0]
        json = {
                "url": item["url"],
                "version": item["version"],
                "describe": item["describe"]
        }
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)
#测试上传图片的接口
@other_api.route('/fm/merchant/v1/uploadimg/', methods=['POST'])
def up():
 try:
    if request.method == 'POST':
        file = request.files['topImage']
        fname, fext = os.path.splitext(file.filename)
        if file:
            filename = '%s%s' % ('test', fext)
            osstr = os.path.dirname(__file__).replace("\\PycharmProjects\\virgin\\app_merchant","/PycharmProjects/virgin")  +'/static/upload/'+filename
            print osstr
            file.save(osstr)
            uu = tool.pimg(osstr)
            u1 = connect.conn.imageIP + uu
            os.remove(osstr)
            print u1
            return Response(u1)
 except Exception , e:
     print e


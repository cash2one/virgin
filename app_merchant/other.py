__author__ = 'hcy'
from flask import Blueprint,render_template,request
from connect import conn
import pymongo
import tools.tools as tool
from bson import  json_util

other_api=Blueprint("other_api",__name__,template_folder='templates')
mongo=conn.mongo_conn()

@other_api.route('/fm/merchant/v1/appversion/')
def appversion():
    item=mongo.android_version.find().sort("addtime",pymongo.DESCENDING)[0]
    json = {
            "url": item["url"],
            "version": item["version"],
            "describe": item["describe"]
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)
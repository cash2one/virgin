__author__ = 'hcy'
from flask import Blueprint,render_template,request
from connect import conn
import pymongo
import tools.tools as tool
from bson import  json_util

other_api=Blueprint("other_api",__name__,template_folder='templates')
mongo=conn.mongo_conn_user()

@other_api.route('/usercenter/v1/register/')
def register():
    item=mongo.user_web.find().sort("addtime",pymongo.DESCENDING)[0]
    json = {
            "url": item["url"],
            "version": item["version"],
            "describe": item["describe"]
    }
    result=tool.return_json(0,"success",json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)


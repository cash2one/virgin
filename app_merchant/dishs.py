#coding=utf-8
__author__ = 'hcy'
from flask import Blueprint,render_template,request
from connect import conn
from bson import ObjectId
import tools.tools as tool
from bson import  json_util
import auto
import os

dishs_api=Blueprint("dishs_api",__name__,template_folder='templates')
mongo=conn.mongo_conn()


@dishs_api.route('/fm/merchant/v1/dishs/dishsclass', methods=['POST'])
def dishsclass():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
        restaurant_id = request.form["restaurant_id"]
    jwtmsg = auto.decodejwt(jwtstr)
    menu=mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"menu.name":1,"menu.id":1,"_id":0})
    json=menu
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)



@dishs_api.route('/fm/merchant/v1/dishs/adddishs', methods=['POST'])
def dishsclass():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
        restaurant_id = request.form["restaurant_id"]
    jwtmsg = auto.decodejwt(jwtstr)
    menu=mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"menu.name":1,"menu.id":1,"_id":0})
    json=menu
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)
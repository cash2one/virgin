#--coding:utf-8--#
_author_='hcy'
from flask import Blueprint,render_template,request
import requests
import urllib2
import json
from connect import conn
from bson import ObjectId,json_util
import tools.public_vew as tool
import tools.auto as auto

mongo=conn.mongo_conn()

test_api = Blueprint('test_api', __name__, template_folder='templates')

@test_api.route('/mongoconn')
def mongoconn():
    list = mongo.restaurant.find_one({"_id":ObjectId("572af8f48831ac19d4e4f282")})
    return  json_util.dumps(list)


@test_api.route('/ttt')
def ttt():
    return render_template("/test/posttest.html")

@test_api.route('/jwt')
def jwt():
    a = auto.encodejwt()
    return a

@test_api.route('/dejwt', methods=['POST'])
def dejwt():
    print 'adshjfgjahsgjihsalkjghlkadshglkh'
    jsonstr = request.form["msg"]
    print jsonstr

    a = auto.decodejwt(jsonstr)
    print a
    return a


@test_api.route('/test')
def test():
    try:
        values="{'title':'Read a book'}";
        headers = {'content-type': 'application/json',"Accept": "application/json"};
        r = requests.post('http://127.0.0.1:5000/foodmap/merchant/api/v1.0/tasks1/',json.dumps(values),headers);
        print r.text;
    except Exception,e:
        print e.message
    # url='http://127.0.0.1:5000/foodmap/merchant/api/v1.0/tasks1'
    # values ={'title':'Smith'}
    # jdata = json.dumps(values)             # 对数据进行JSON格式化编码
    # req = urllib2.Request(url, jdata)       # 生成页面请求的完整数据
    # response = urllib2.urlopen(req)       # 发送页面请求
    # return response.read()
    # return  render_template('/test.html')

@test_api.route('/getroomslist', methods=['GET'])
def getroomslist():
    list = tool.getroomslist("572af8f48831ac19d4e4f282")
    return json_util.dumps(list)



@test_api.route('/gepostcanshu', methods=['POST'])
def gepostcanshu():
    username=request.form['username']
    print username
    list = tool.getroomslist("572af8f48831ac19d4e4f282")
    return json_util.dumps(list)


@test_api.route('/testfrom', methods=['POST'])
def testfrom():
    return  render_template("posttest.html")
#--coding:utf-8--#
_author_='hcy'
from connect import conn
from bson.objectid import  ObjectId
from bson.json_util import dumps

mongo=conn.mongo_conn()

# [通用方法] 获取包房列表
#  可用在“餐位管理”、“订座管理”、“订餐管理”
def getroomlist(restaurantid):
    print restaurantid
    restaurant = mongo.restaurant.find_one({"_id":ObjectId(restaurantid)},{"rooms":1})
    roomlist = restaurant["rooms"]
    print roomlist
    rooms=[]

    # for item in restaurant:
    #     print item
    #     i={}
    #     # i["name"]=item["room_name"]
    #     rooms.append(i)
    return rooms
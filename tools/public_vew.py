#--coding:utf-8--#
_author_='hcy'
from connect import conn
from bson import ObjectId,json_util
# import json

mongo=conn.mongo_conn()

def getroomslist(restaurant_id):
    rooms=mongo.restaurant.find_one({"_id":ObjectId(restaurant_id)},{"rooms":1})
    a=json_util.loads(json_util.dumps(rooms))
    b = a["rooms"]
    type_list=[]
    for i in b:
        if i["room_people_name"] not in type_list:
            type_list.append(i["room_people_name"])
    list=[]
    for a in type_list:
        room={}
        room["room_people_num"]=a
        rooms=[]
        for i1 in b:
            if i1["room_people_name"]==a:
                item={}
                item["room_id"]=i1["room_id"]
                item["room_name"]=i1["room_name"]
                rooms.append(item)
        room["room_count"]=rooms
        list.append(room)

    print json_util.dumps(list)
    return rooms

# {
#     "name": "2-4人包房",
#     "rooms": [
#         {
#             "room_name": "123",
#             "room_id": "201605060916175013",
#         },
#         {
#             "room_name": "123",
#             "room_id": "201605060916175013",
#         }
#     ]
# }
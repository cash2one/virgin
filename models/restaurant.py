# --coding:utf-8--#
_author_ = 'hcy'
from connect import conn
from bson import ObjectId
import json

mongo = conn.mongo_conn()


class R_format:
    @staticmethod
    def getroomslist(db_json, json_list=None):
        a = json.loads(json.dumps(db_json))
        b = a["rooms"]
        type_list = []
        for i in b:
            if i["room_people_name"] not in type_list:
                type_list.append(i["room_people_name"])
        format_data = []
        for a in type_list:
            room = {"room_people_num": a}
            rooms = []
            for i1 in b:
                if i1["room_people_name"] == a:
                    item = {"room_id": i1["room_id"], "room_name": i1["room_name"]}
                    rooms.append(item)
            room["room_count"] = rooms
            format_data.append(room)
        return format_data


class get_Room:
     @staticmethod
     def db_room(id):
         rooms = mongo.restaurant.find_one({"_id": ObjectId(id)}, {"rooms": 1})
         return R_format.getroomslist(rooms)


if __name__ == '__main__':
    get_Room.db_room(123)
    pass

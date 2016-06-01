# coding=utf-8
from connect.conn import mongo_conn
from connect.mongotool import MongoAPI
from bson import ObjectId, json_util
import json

__author__ = 'dolacmeo'
__doc__ = '用户评论数据处理'

test_ex = {
    'restaurant_id': '9as87df90hjgkghjkf9as87df9',
    'dish_id': '67asd5f765sdfg7f587',
    'order_id': '89asasdf9087a09sdf77',
    'user_id': 'asd89f787asdfsdf9',
    'user_info': {'user_name': '张全蛋', 'user_head': 'A98SD234568A7SDF987'},
    'post_date': 120937494517,
    'rating': {'total': 4, 'taste': 3, 'env': 3, 'service': 3},
    'comment_text': '<div><em>我是富土康三号流水线的质检员</em></div>',
    'comment_pic': [{'id': '7a89sdf709a8f7', 'md5': 'A8SD7F86A8D7F6'},
                    {'id': '7a89sdf70asdf7', 'md5': 'A8SD1234asdfv6'}]
}


class Comment(MongoAPI):
    def __init__(self):
        MongoAPI.__init__(self, mongo_conn().comment)
        pass

    def add(self, json_data):
        try:
            self.conn.insert(json_data)
            if json_data['rating']['total'] < 3:
                rating = {'$inc': {'rating.down': 1}}
            else:
                rating = {'$inc': {'rating.up': 1}}
            mongo_conn().restaurant.update({'_id': ObjectId(json_data['restaurant_id'])}, rating)
            return True
        except Exception, e:
            print e
            return False

    def find(self, json_data):
        try:
            if 'comment_id' in json_data.keys():
                db_data = self.conn.find_one({"_id": ObjectId(json_data['comment_id'])})
                db_data['_id'] = str(db_data['_id'])
                return json.loads(json_util.dumps(db_data))
            elif 'restaurant_id' in json_data.keys():
                db_data = self.conn.find({"restaurant_id": ObjectId(json_data['restaurant_id'])})
            elif 'dish_id' in json_data.keys():
                db_data = self.conn.find({"dish_id": ObjectId(json_data['dish_id'])})
            elif 'order_id' in json_data.keys():
                db_data = self.conn.find({"order_id": ObjectId(json_data['order_id'])})
            elif 'user_id' in json_data.keys():
                db_data = self.conn.find({"user_id": ObjectId(json_data['user_id'])})
            else:
                return False
            new = []
            for n in db_data:
                new_data = {}
                for key in n.keys():
                    # print key
                    if key == '_id':
                        new_data[key] = str(n[key])
                    elif key == 'restaurant_id':
                        new_data[key] = str(n[key])
                    elif key == 'user_id':
                        new_data[key] = str(n[key])
                    else:
                        new_data[key] = n[key]
                new.append(new_data)
            if new is not None:
                return json.loads(json_util.dumps(new))
            else:
                return False
        except Exception, e:
            print e
            return False
        pass

    pass


if __name__ == '__main__':
    c = Comment()
    # c.add(test_ex)
    print json.dumps(c.find({'restaurant_id': '57329d530c1d9b2f4c85f8e5'}), indent=2)
    pass

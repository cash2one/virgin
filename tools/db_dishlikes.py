# coding=utf-8
from connect.conn import mongo_conn
from connect.mongotool import MongoAPI
from bson import ObjectId, json_util
from datetime import datetime
import json

__author__ = 'dolacmeo'


class DishLikes(MongoAPI):
    def __init__(self):
        MongoAPI.__init__(self, mongo_conn().dish_likes)
        pass

    def addlike(self, json_data):
        try:
            for key in ['user_id', 'dish_id', 'restaurant_id']:
                if key not in json_data.keys():
                    return {'success': True, 'error': '%s is not in request' % key}
            json_data['is_like'] = True
            json_data['timestamp'] = datetime.now()
            is_success = self.conn.insert(json_data)
            return {'success': True, '_id': str(is_success)}
        except Exception, e:
            return {'success': True, 'error': e}

    def dislike(self, json_data):
        try:
            self.conn.remove(json_data)
            return {'success': True}
        except Exception, e:
            return {'success': True, 'error': e}
        pass

    def findlikes(self, json_data):
        try:
            is_success = self.conn.find(json_data)
            is_success = json_util.loads(json_util.dumps(is_success))
            if is_success:
                from tools import Restaurant
                for like in is_success:
                    like['name'] = Restaurant({'dish_id': like['dish_id']}).info('name')
                    if not like['name']:
                        like['name'] = ''
                    like['img'] = Restaurant({'dish_id': like['dish_id']}).info('guide_image')
                    if not like['img']:
                        like['img'] = ''
                    like['_id'] = str(like['_id'])
                    like['timestamp'] = like['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            return {'success': True, 'data': is_success}
        except Exception, e:
            return {'success': True, 'error': e}
        pass

    def shoplikes(self, json_data):
        try:
            from tools import Restaurant
            menus = Restaurant({'_id': json_data['restaurant_id']}).get_item('menu')
            all_dishes = []
            for menu in menus:
                for dish in menu['dishs']:
                    is_like = self.conn.find({'dish_id': dish['id']}).count()
                    # print dish['name'], is_like
                    if is_like > 0:
                        all_dishes.append({'likes': is_like, 'name': dish['name'], 'image': dish['guide_image']})
            return {'success': True, 'data': all_dishes}
        except Exception, e:
            return {'success': True, 'error': e}
        pass

    pass


if __name__ == '__main__':
    d = DishLikes()
    # print d.addlike({'user_id': 'asdfqerqerzcxvadfg', 'dish_id': '123415sdgsfghdgfh', 'restaurant_id': 'asdgvzxcbsfgsfg'})
    # print d.dislike({'user_id': 'asdfqerqerzcxvadfg', 'dish_id': '123415sdgsfghdgfh', 'restaurant_id': 'asdgvzxcbsfgsfg'})
    d.shoplikes({'restaurant_id': '574c0f570c1d9b34780b6d4d'})
    pass

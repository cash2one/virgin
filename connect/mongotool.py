# coding=utf-8

from bson import ObjectId, json_util
from flask import json

_author_ = 'dolacmeo'


class MongoAPI:
    __doc__ = """
    Mongo数据库接口:
    插入数据 add   : 直接插入数据
    查找数据 find  : 必须包含'_id'键
    修改数据 fix   : 必须包含'_id'键 修改时需包含{'fix_data': {'key': 'value'}}
    删除数据 remove: 必须包含'_id'键"""

    def __init__(self, conn):
        """初始化需要实例化数据接口
        :type conn: def
        """
        self.conn = conn
        pass

    def add(self, json_data):
        """插入数据: 直接插入字典json_data
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.insert(json_data)
            return {'success': True, '_id': str(json_data['_id'])}
        except Exception, e:
            return {'success': False, 'error': e}

    def find(self, json_data):
        """查找数据: 允许返回多条数据
        :param json_data: :type json_data:dict
        """
        db_data = self.conn.find(json_data)
        return json.loads(json_util.dumps(db_data))

    def find_id(self, json_data):
        """查找数据: 必须包含json_data._id
        :param json_data: :type json_data:dict
        """
        db_data = self.conn.find_one({"_id": ObjectId(json_data['_id'])})
        db_data['_id'] = str(db_data['_id'])
        return json.loads(json_util.dumps(db_data))

    def fix(self, json_data):
        """修改数据: 必须包含json_data._id 修改数据json_data.fix_data
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.update_one({"_id": ObjectId(json_data['_id'])},
                                 {"$set": json_data['fix_data']})
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}

    def remove(self, json_data):
        """删除数据: 必须包含json_data._id
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.remove(json_data)
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}
        pass

    def remove_id(self, _id):
        """删除数据: 必须包含json_data._id
        :param _id: ObjectId :type _id:str
        """
        try:
            self.conn.remove({"_id": ObjectId(_id)})
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}
        pass

    pass
# coding=utf-8
from bson import json_util
import datetime
__author__ = 'dolacmeo'
__doc__ = 'Mongo-Database conn'

user_name = 'FoodMap32loK22Nk3oO_adm9n'
pass_word = 'UK#45JEIksiJEwi(209Y*nOwm'
address = '125.211.222.237:27638'
db_name = 'db_foodmap'


def mongo_conn(user=user_name, psw=pass_word, add=address, db=db_name):
    from flask_pymongo import MongoClient
    db_url = 'mongodb://{0}:{1}@{2}/{3}?authmechanism=SCRAM-SHA-1'\
             .format(user, psw, add, db)
    return MongoClient(db_url)[db_name]


class MongoHelp:
    # 数据库操作模块
    def __init__(self, db_conn):
        self.conn = db_conn
        self.the_data = None

    def id_format(self, data=None):
        # 格式化数据库返回数据
        # 会格式化ISO时间、mongodb_id 并转换数据为json字典
        if not data:
            data = self.the_data
        the_order = json_util.loads(json_util.dumps(data))
        if isinstance(the_order, list):
            for n in range(len(the_order)):
                try:
                    the_order[n]['_id'] = str(the_order[n]['_id'])
                    for k in the_order[n].keys():
                        if isinstance(the_order[n][k], datetime.datetime):
                            the_order[n][k] = the_order[n][k].strftime('%Y-%m-%d %H:%M:%S')
                except Exception, e:
                    pass
            return the_order
        else:
            if the_order is None:
                return None
            try:
                the_order['_id'] = str(the_order['_id'])
                for k in the_order.keys():
                    if isinstance(the_order[k], datetime.datetime):
                        the_order[k] = the_order[k].strftime('%Y-%m-%d %H:%M:%S')
            except Exception, e:
                pass
            return the_order

    @property
    def db_data(self):
        # 通过此方法判断数据是否合法
        if self.the_data:
            return self.id_format()
        else:
            return None

    def insert(self, json_data):
        # 插入数据
        the_order = self.conn.insert(json_data)
        return {'status': 'new', '_id': str(the_order)}

    def find(self, ident_json):
        # 查找多个
        self.the_data = self.conn.find(ident_json)
        return self.db_data

    def find_one(self, ident_json):
        # 查找一个
        self.the_data = self.conn.find_one(ident_json)
        return self.db_data

    def fix(self, ident_json, json_data):
        # 修改多个数据
        self.the_data = self.conn.update(ident_json, {'$set': json_data})
        # return json_util.loads(json_util.dumps(self.the_data))['updatedExisting']
        return self.db_data['updatedExisting']

    def fix_one(self, ident_json, json_data):
        # 修改一个数据
        self.the_data = self.conn.update_one(ident_json, {'$set': json_data}).raw_result
        # return json_util.loads(json_util.dumps(self.the_data))['updatedExisting']
        return self.db_data['updatedExisting']

    def remove(self, ident_json):
        # 删除数据
        the_order = self.conn.remove(ident_json)
        the_order = json_util.loads(json_util.dumps(the_order))
        return True if the_order['ok'] >= 1 else False

    pass


if __name__ == '__main__':
    pass
    m = MongoHelp(mongo_conn().restaurant)
    print m.find({"_id":ObjectId("57329b1f0c1d9b2f4c85f8e3")})
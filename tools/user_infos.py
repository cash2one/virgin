# coding=utf-8
import datetime
import requests
from connect import conn
from bson import ObjectId, json_util
import json

_author_ = 'dolacmeo'


class GetUser:
    # SMSnetgate = 'http://125.211.222.237:10031'
    SMSnetgate = 'http://127.0.0.1:10032'

    def __init__(self, params):
        self.params = params
        self.is_admin, self.is_user = False, False
        self.user_center_conn = conn.mongo_conn_user().user_web
        self.restaurant_conn = conn.mongo_conn().restaurant
        self.center_info = self.get_center_info()
        if self.center_info:
            self.user_center_id = str(self.center_info['_id'])
        else:
            self.user_center_id = None

    def __appid(self, sub_appid):
        self.is_admin, self.is_user = False, False
        if '1' in sub_appid.keys():
            self.is_admin = True
        if '2' in sub_appid.keys():
            self.is_user = True

    def validate(self):
        if '1' in self.center_info['appid'].keys():
            self.is_admin = True
            if self.sms_validate():
                self.validity = True
                self.user_center_conn.update_one({"_id": ObjectId(self.user_center_id)},
                                                 {"$set": {"ident": self.params['ident'],
                                                           "time": datetime.datetime.now()}})
                self.shop_info = self.restaurant_conn.find({"user": {"$in": [ObjectId(self.user_center_id)]}})
                if self.shop_info:
                    self.shop_info = self.shop_info[0]
                else:
                    self.shop_info = None
            else:
                self.validity = False
        if '2' in self.center_info['appid'].keys():
            self.is_user = True
            if self.params['password'] == self.center_info['registeruser']['password']:
                self.validity = True
                self.user_center_conn.update_one({"_id": ObjectId(self.user_center_id)},
                                                 {"$set": {"ident": self.params['ident'],
                                                           "time": datetime.datetime.now()}})
            else:
                self.validity = False

    def send_sms(self):
        import random
        if self.is_admin:
            data = {'sign': '美食地图',
                    'tpl': 'SMS_8161119',
                    'param': json.dumps({"code": str(random.randint(1000000, 9999999))[1:]}),
                    'tel': self.params['phone'],
                    'ex': self.params['ex']
                    }
            req = requests.post(self.SMSnetgate + '/sms.send', data)
            return req.json()
        else:
            return {'success': False}
        pass

    def sms_validate(self):
        data = {'tel': self.params['phone'],
                'ex': self.params['ex'],
                'tpl': self.params['tpl'],
                'code': self.params['code']}
        req = requests.post(self.SMSnetgate + '/sms.validate', data)
        return req.json()['success']

    def get_center_info(self):
        found = self.user_center_conn.find({'phone': self.params['phone']})
        found = json_util.loads(json_util.dumps(found))
        if found:
            self.__appid(found[0]['appid'])
            return found[0]
        else:
            return None

    @property
    def admin_shop_id(self):
        self.validate()
        if self.is_admin:
            if self.sms_validate():
                return {'success': True, 'id': str(self.shop_info['_id']), 'name': self.shop_info['name']}
            else:
                return {'success': False, 'info': 'sms code ERROR'}
        else:
            return {'success': False, 'info': 'user ERROR'}
    pass


if __name__ == '__main__':
    # u = GetUser({'phone': '15645678759',
    #              'ident': '',
    #              'ex': '#foodmap.mobile',
    #              'tpl': 'SMS_8161119',
    #              'code': '272609'})
    # print u.is_admin
    # print u.send_sms()
    # print u.admin_shop_id
    pass

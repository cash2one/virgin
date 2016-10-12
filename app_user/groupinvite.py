# coding=utf-8
import datetime
import time
import json
from flask import Blueprint, render_template, request, abort

from connect import conn
from connect.mongotool import MongoHelp, mongo_conn
from app_merchant import auto
from bson import json_util
import tools.tools as tool
from flasgger import swag_from
from tools.swagger import swagger

__author__ = 'dolacmeo'

restaurant = MongoHelp('restaurant')
db_info = MongoHelp('qingke')
db_order = MongoHelp('order_groupinvite')
mongo=conn.mongo_conn()

# 'wait_friends', 'wait_pay', 'already_payment', 'already_used', 'time_out'


class GroupInvite:
    def __init__(self, mod='list'):
        self.mod = mod
        if mod == 'list':
            self.all_item = self.__item_list()
        elif len(mod) == 6:
            self.code = mod
            self.invite_order = self._find_code_invite(self.code)
            self._id = self.invite_order['group_id']
            self.the_invite = self.__format_db_info(db_info.find_one({'_id': self._id}))
        elif len(mod) == 24:
            self.the_invite = self.__format_db_info(db_info.find_one({'_id': mod}))
            if self.the_invite:
                self._id = mod
            else:
                self._id = None
        else:
            raise Exception('mod need mongo_id or invite_code inside')
        pass

    def __str__(self):
        if self.mod == 'list':
            return str(self.all_item)
        else:
            return str(self.the_invite)

    @staticmethod
    def __format_db_info(data):
        if not data:
            return None
        if data['seltime'] == '0':
            time_range = '10:30'
        elif data['seltime'] == '1':
            time_range = '16:00'
        else:
            time_range = 'NULL'
        new_data = dict(_id=data['_id'],
                        restaurant=dict(rid=data['nid'], name=data['name'], dist=data['sq'],
                                        types='|'.join([x['name'] for x in data['lx']]),
                                        pic=data['pic'], addr=data['address'], phone=data['phone']),
                        group_info=dict(size=int(data['nr']), total=int(data['cou']), available=0),
                        price=dict(now=float(data['price']), old=float(data['zj'])),
                        detail=data['summary'], time_range=time_range,
                        the_time=dict(show=data['time'], start=data['time1'], end=data['time2']),
                        menu=data['menulist'])
        orders = db_order.find({'group_id': new_data['_id']})
        available_num = new_data['group_info']['total']
        for m in orders:
            if m['status'] in ['wait_friends', 'wait_pay', 'already_payment', 'already_used']:  # 定义不可抢状态
                available_num -= 1
        new_data['group_info']['available'] = available_num
        return new_data

    @staticmethod
    def _find_code_invite(code):
        the_invite = db_order.find_one({'invite_code': code,
                                        'end_time': {"$gte": datetime.datetime.fromtimestamp(time.time())}})
        return the_invite

    def __item_list(self):

        # 展示定义: 展示时间 》 结束时间前一天
        now_list = db_info.find_sort({
            'time': {"$lt": datetime.datetime.fromtimestamp(time.time() - 86400)},
            'time2': {"$gte": datetime.datetime.fromtimestamp(time.time() + 86400)}
        }, 'time')
        if now_list:
            for n in range(len(now_list)):
                self._check_all_order_time(now_list[n]['_id'])
                now_list[n] = self.__format_db_info(now_list[n])
            return now_list
        else:
            return []

    @staticmethod
    def _get_invite(_id):
        return GroupInvite.__format_db_info(db_info.find_one({'_id': _id}))

    def _is_invite_open(self, _id=None):
        if _id:
            the_id = _id
        else:
            the_id = self._id
        orders = db_order.find({'group_id': the_id})
        for n in orders:
            if time.time() - time.mktime(time.strptime(n['start_time'], "%Y-%m-%d %H:%M:%S")) >= 2700:
                db_order.fix_one({'group_id': the_id, 'invite_code': n['invite_code']}, {'status': 'timeout'})
        all_info = self.__format_db_info(db_info.find_one({'_id': the_id}))
        if time.mktime(time.strptime(all_info['the_time']['end'], '%Y-%m-%d %H:%M:%S')) - time.time() <= 0:
            return 0
        available_num = all_info['group_info']['total']
        for m in orders:
            if m['status'] in ['wait_friends', 'else']:  # 定义不可抢状态
                available_num -= 1
        return available_num

    def _is_invited(self, user_id, _id=None):
        if _id:
            the_id = _id
        else:
            the_id = self._id
        is_master = db_order.find({'group_id': the_id, 'master_id': user_id,
                                   'status': {'$in': ['wait_friends', 'wait_pay', 'already_payment', 'already_used']}})
        if not is_master:  # 当前限制 不可多次发起
            return False
        else:
            return True
        # 未启用限制 发起后不允许再被邀请
        # invited = db_order.find({'group_id': the_id, 'friends': {'$in': [user_id]}})
        # if not(is_master or invited):
        #     return False
        # else:
        #     return True
        pass

    def new_invite(self, master_id):
        if (not self._id) or not master_id:
            raise Exception('mod need mongo_id and master_id inside')
        import random
        insert_data = {
            'order_id': "MSDT%s%03d" % (int(time.time() * 1000), random.randint(1, 999)),
            'group_id': self._id,
            'master_id': master_id,
            'status': 'wait_friends',
            'max_group': self.the_invite['group_info']['size'],
            'invite_code': "%06d" % random.randint(0, 999999),
            'start_time': datetime.datetime.now(),
            'end_time': datetime.datetime.strptime(self.the_invite['the_time']['end'], "%Y-%m-%d %H:%M:%S"),
            'friends': [],
            'restaurant_info': self.the_invite['restaurant'],
            'dishes': self.the_invite['menu'],

            # 'addtime':datetime.datetime.now()
        }
        available_num = self._is_invite_open(self._id)
        if self._is_invite_open(self._id):
            if not self._is_invited(master_id):
                is_insert = db_order.insert(insert_data)
            else:
                return {'_id': '', 'code': '', 'error': 'already in the invite'}
        else:
            return {'_id': '', 'code': '', 'error': 'available_num is %s' % available_num}
        if is_insert:
            return {'_id': is_insert, 'code': insert_data['invite_code'], 'error': ''}
        else:
            return {'_id': '', 'code': '', 'error': 'cant inster: %s' % is_insert}

    def mark_timeout(self, order_data=None):
        if not order_data:
            order_data = self.invite_order
            _id = self._id
            code = self.code
        else:
            _id = order_data['group_id']
            code = order_data['invite_code']
        if time.time() - time.mktime(time.strptime(order_data['start_time'], "%Y-%m-%d %H:%M:%S")) >= 2700:
            db_order.fix_one({'group_id': _id, 'invite_code': code}, {'status': 'timeout'})
            if not order_data:
                self.invite_order = self._find_code_invite(code)
            else:
                return self._find_code_invite(code)

    def _check_all_order_time(self, invent_id):
        all_data = db_order.find({'group_id': invent_id, 'status':
                                 {'$in': ['wait_friends', 'wait_pay', 'already_payment']}})
        for n in all_data:
            self.mark_timeout(n)

    def follow(self, user_id):
        if not user_id or (user_id == self.invite_order['master_id']):
            raise Exception('mod need user_id inside or the user is master')
        self.mark_timeout()
        if self.invite_order['status'] == 'timeout':
            return {'success': False, 'error': 'timeout! start_time: %s' % self.invite_order['start_time']}
        if self.invite_order['max_group'] - len(self.invite_order['friends']) >= 2:
            #song
            get_in = mongo.order_groupinvite.update_one({'group_id': self._id, 'invite_code': self.code},
                                        {"$addToSet": {"friends": user_id}})
            if self.invite_order['max_group'] - len(self.invite_order['friends']) == 2:
                db_order.fix_one({'group_id': self._id, 'invite_code': self.code},
                                 {'status': 'wait_pay'})#'addtime':datetime.datetime.now()
            return {'success': True, 'error': ''}
        else:
            return {'success': False, 'error': 'max group'}

    def make_payment(self, service='alipay'):
        self.mark_timeout()
        if self.invite_order['status'] == 'wait_pay':
            # 此处加入支付流程
            print service
            set_mark = db_order.fix_one({'group_id': self._id, 'invite_code': self.code},
                                        {'status': 'already_payment'})
            return {'success': set_mark, 'error': ''}
        else:
            return {'success': False, 'error': 'status: %s' % self.invite_order['status']}

    def mark_used(self):
        # 需要补充已付款未消费但已超时的订单 操作逻辑
        if self.invite_order['status'] == 'already_payment':
            set_mark = db_order.fix_one({'group_id': self._id, 'invite_code': self.code},
                                        {'status': 'already_used'})
            return {'success': set_mark, 'error': ''}
        else:
            return {'success': False, 'error': 'status: %s' % self.invite_order['status']}

    @property
    def app_invite_list(self):
        new_data = dict(time_range=[])
        data = self.__item_list()
        for n in data:
            m = dict(_id=n['_id'],
                     img=n['restaurant']['pic'],
                     name=n['restaurant']['name'],
                     dist=n['restaurant']['dist'],
                     new_price=n['price']['now'],
                     old_price=n['price']['old'],
                     size=n['group_info']['size'],
                     available=n['group_info']['available'])
            if n['time_range'] not in new_data['time_range']:
                new_data['time_range'].append(n['time_range'])
                new_data[n['time_range']] = [m]
            elif n['time_range'] in new_data['time_range']:
                new_data[n['time_range']].append(m)
            else:
                pass
        # del new_data['time_range']
        return [{'time': '10:30', 'data': new_data['10:30']},
                {'time': '16:00', 'data': new_data['16:00'] if '16:00' in new_data['time_range'] else []}]

    pass


# jwt装饰器 只支持‘post’
def jwt_data(func):
    def _jwt_data(*args, **kwargs):
        if request.method == 'POST':
            if auto.decodejwt(request.form['jwtstr']):
                try:
                    data = func(*args, **kwargs)
                    if isinstance(data, list):
                        r = dict(list=data)
                        result = tool.return_json(0, "success", True, r)
                        return json_util.dumps(result, ensure_ascii=False, indent=2)
                    elif isinstance(data, dict):
                        result = tool.return_json(0, "success", True, data)
                        return json_util.dumps(result, ensure_ascii=False, indent=2)
                except Exception, e:
                    print e
                    result = tool.return_json(0, "field", True, str(e))
                    return json_util.dumps(result, ensure_ascii=False, indent=2)
            else:
                result = tool.return_json(0, "field", False, None)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            return abort(403)

    return _jwt_data


group_invite = Blueprint("group_invite", __name__, template_folder='templates')
group_invite_list = swagger("2 开团请客", "获取请客列表")
group_invite_list_json = {
    "auto": group_invite_list.String(description='验证是否成功'),
    "message": group_invite_list.String(description='SUCCESS/FIELD', default="SUCCESS"),
    "code": group_invite_list.Integer(description='h', default=0),
}
group_invite_list.add_parameter(name='jwtstr', parametertype='formData', type='string', required=True,
                                description='jwt串',
                                default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')

HOMEBASE = '/fm/user/v1/groupinvite'


@group_invite.route(HOMEBASE, methods=['POST'])
@swag_from(group_invite_list.mylpath(schemaid='group_invite_list', result=group_invite_list_json))
@jwt_data
def get_groupinvite_list():
    # 获取请客列表
    return GroupInvite().app_invite_list


group_invite_detail = swagger("2-1 开团请客详情", "获取请客详情")
group_invite_detail_json = {
    "auto": group_invite_detail.String(description='验证是否成功'),
    "message": group_invite_detail.String(description='SUCCESS/FIELD', default="SUCCESS"),
    "code": group_invite_detail.Integer(description='h', default=0),


}
group_invite_detail.add_parameter(name='jwtstr', parametertype='formData', type='string', required=True,
                                  description='jwt串',
                                  default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
group_invite_detail.add_parameter(name='group_id', parametertype='formData', type='string', required=True,
                                  description='开团信息的数据库id', default='57c53441612c5e14344b3fec')


@group_invite.route(HOMEBASE + "/detail", methods=['POST'])
@swag_from(group_invite_detail.mylpath(schemaid='group_invite_detail', result=group_invite_detail_json))
def get_groupinvite_detail():
    # 获取请客详情
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = GroupInvite(request.form['group_id']).the_invite
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            except Exception, e:
                print e
                result = tool.return_json(0, "field", True, str(e))
                return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


groupinvite_neworder = swagger("2-2-1 抢优惠", "抢优惠")
groupinvite_neworder_json = {
    "auto": groupinvite_neworder.String(description='验证是否成功'),
    "message": groupinvite_neworder.String(description='SUCCESS/FIELD', default="SUCCESS"),
    "code": groupinvite_neworder.Integer(description='h', default=0),
}
groupinvite_neworder.add_parameter(name='jwtstr', parametertype='formData', type='string', required=True,
                                   description='jwt串',
                                   default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
groupinvite_neworder.add_parameter(name='group_id', parametertype='formData', type='string', required=True,
                                   description='开团信息的数据库id', default='57c53441612c5e14344b3fec')
groupinvite_neworder.add_parameter(name='user_id', parametertype='formData', type='string', required=True,
                                   description='用户id', default='5747bd310b05552c4c571810')


@group_invite.route(HOMEBASE + '/neworder', methods=['POST'])
@swag_from(groupinvite_neworder.mylpath(schemaid='groupinvite_neworder', result=groupinvite_neworder_json))
def groupinvite_neworder():
    # 抢资格
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                data = GroupInvite(request.form['group_id']).new_invite(request.form['user_id'])
                # print data
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            # except Exception, e:
            #     print e
            #     result = tool.return_json(0, "field", True, str(e))
            #     return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


groupinvite_add_friend = swagger("2-3 邀请好友", "抢优惠")
groupinvite_add_friend_json = {
    "auto": groupinvite_add_friend.String(description='验证是否成功'),
    "message": groupinvite_add_friend.String(description='SUCCESS/FIELD', default="SUCCESS"),
    "code": groupinvite_add_friend.Integer(description='h', default=0),
}

groupinvite_add_friend.add_parameter(name='jwtstr', parametertype='formData', type='string', required=True,
                                     description='jwt串',
                                     default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
groupinvite_add_friend.add_parameter(name='code', parametertype='formData', type='string', required=True,
                                     description='开团邀请码', default='675120')
groupinvite_add_friend.add_parameter(name='user_id', parametertype='formData', type='string', required=True,
                                     description='用户id', default='5747bd310b05552c4c571810')


@group_invite.route(HOMEBASE + '/add_friend', methods=['POST'])
@swag_from(groupinvite_add_friend.mylpath(schemaid='groupinvite_add_friend', result=groupinvite_add_friend_json))
def groupinvite_add_friend():
    # 接受邀请
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                data = GroupInvite(request.form['code']).follow(request.form['user_id'])
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            # except Exception, e:
            #     print e
            #     result = tool.return_json(0, "field", True, str(e))
            #     return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


groupinvite_order = swagger("2-3-2 老用户查看状态", "开团订单详情")
groupinvite_order_json = {
    "auto": groupinvite_order.String(description='验证是否成功'),
    "message": groupinvite_order.String(description='SUCCESS/FIELD', default="SUCCESS"),
    "code": groupinvite_order.Integer(description='h', default=0),
    "data":{
        "status": group_invite_detail.String(description='wait_friends待邀请, wait_pay待支付, already_payment已支付, already_used已使用, time_out超时', default="timeout"),
        "master_id": group_invite_detail.String(description='发起人id', default="dola"),
        "dishes": [
          {
            "flname":  group_invite_detail.String(description='分类名', default="111"),
            "allcount":  group_invite_detail.Integer(description='全部数量', default=2),
            "flnum": group_invite_detail.String(description='分类数', default="0"),
            "ff": group_invite_detail.String(description='1', default="1"),
            "cp": [
              {
                "count": group_invite_detail.String(description='菜品数量', default="1"),
                "price": group_invite_detail.String(description='价格', default="19.0"),
                "allprice": group_invite_detail.String(description='总价', default="19.0"),
                "id": group_invite_detail.String(description='菜品id', default="201605120931222746"),
                "name": group_invite_detail.String(description='菜名', default="骨架")
              }
            ],
            "fl": group_invite_detail.String(description='分类', default="fl1")
          }
        ],
        "max_group": group_invite_detail.Integer(description='h', default=5),
        "order_id": group_invite_detail.String(description='订单id', default="MSDT1472541303927956"),
        "start_time": group_invite_detail.String(description='开始时间', default="2016-08-30 15:15:03"),
        "invite_code": group_invite_detail.String(description='邀请码', default="603101"),
        "_id": group_invite_detail.String(description='开团id', default="57c532770b0555090830ff50"),
        "restaurant_info": {
          "rid": group_invite_detail.String(description='饭店id', default="5733dc610c1d9b310dd05549"),
          "pic": group_invite_detail.String(description='饭店图', default="1a7f2ae4c0db98e3481f9670c0e6d7dc"),
          "dist": group_invite_detail.String(description='商圈', default="抚顺街"),
          "addr": group_invite_detail.String(description='地址', default="哈尔滨市道里区安平街18号"),
          "name": group_invite_detail.String(description='饭店名', default="快捷熏酱饺子"),
        },
        "end_time": group_invite_detail.String(description='结束时间', default="2017-09-30 10:35:00"),
        "group_id": group_invite_detail.String(description='分组id', default="57c4dc7c612c5e1a7435ec35"),
        "friends": group_invite_detail.String(description='朋友列表', default="['5747bd310b05552c4c571865']"),
  }
}

groupinvite_order.add_parameter(name='jwtstr', parametertype='formData', type='string', required=True,
                                description='jwt串',
                                default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
groupinvite_order.add_parameter(name='code', parametertype='formData', type='string', required=True,
                                description='开团邀请码', default='735178')


@group_invite.route(HOMEBASE + '/order/detail', methods=['POST'])
@swag_from(groupinvite_order.mylpath(schemaid='groupinvite_order', result=groupinvite_order_json))
def groupinvite_order():
    # 获取订单详情
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                # 'wait_friends', 'wait_pay', 'already_payment', 'already_used', 'time_out'
                data = GroupInvite(request.form['code']).invite_order
                print type(data)
                # print time.strptime(data['addtime'], "%Y-%m-%d %H:%M:%S")
                #song
                if data['status'] == 'wait_friends':
                    data['msg'] ="还有"+str(45-int((datetime.datetime.now()-datetime.datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S")).total_seconds()/60))+"分钟，还需要"+str(data['max_group']-1-len(data['friends']))+"位客人"
                elif data['status'] == 'wait_pay':
                    data['msg'] ="还有"+str(45-int((datetime.datetime.now()-datetime.datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S")).total_seconds()/60))+"分钟付款时间"
                elif data['status'] == 'timeout':
                    if data['max_group']-1-len(data['friends']) == 0:
                        data['msg'] ="付款超时"
                    else:
                        data['msg'] ="45分钟内未邀请到"+str(data['max_group'])+"位好友"
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            except Exception, e:
                print e
                result = tool.return_json(0, "field", True, str(e))
                return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


@group_invite.route(HOMEBASE + '/order/pay', methods=['POST'])
def groupinvite_order_pay():
    # 获取订单详情
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = GroupInvite(request.form['code']).make_payment(request.form['pay_service'])
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            except Exception, e:
                print e
                result = tool.return_json(0, "field", True, str(e))
                return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


@group_invite.route(HOMEBASE + '/order/used', methods=['POST'])
def groupinvite_order_used():
    # 获取订单详情
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = GroupInvite(request.form['code']).mark_used()
                result = tool.return_json(0, "success", True, data)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            except Exception, e:
                print e
                result = tool.return_json(0, "field", True, str(e))
                return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


if __name__ == '__main__':
    # print GroupInvite('57c53441612c5e14344b3fec')
    # print GroupInvite.get_invite('57c4dc7c612c5e1a7435ec35')
    # print GroupInvite('57c4dc7c612c5e1a7435ec35').new_invite('dola')
    # print GroupInvite('205314').follow('dolacmeo')
    # print GroupInvite('205314').mark_used()
    print json_util.dumps(GroupInvite().all_item,ensure_ascii=False,indent=2)
    pass

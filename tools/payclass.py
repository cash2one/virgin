# coding=utf-8
from connect.mongotool import MongoHelp

__author__ = 'dolacmeo'
__doc__ = 'DEMO 实例测试'


class PayOrder:
    def __init__(self, order_id=None):
        self.__order_conn = MongoHelp('order')
        self.__group_order_conn = MongoHelp('order_groupinvite')
        self.__conn = MongoHelp('payOrder')
        if order_id :
            print '11111111111111111'
            self.payorder_id = order_id
            self.payorder = self.__conn.find_one({'_id': order_id})
        else:
            self.payorder = {}
            self.payorder_id = ''
        pass

    def __new_order(self, subject, body, reqfrom, total_fee, order_id, ext_data, ext=''):
        import time
        import datetime
        the_order = {
            "orderid": "MSDT" + datetime.datetime.now().strftime('%Y%m%d') + str(time.time()).replace('.', ''),
            "subject": subject,
            "body": body,
            "reqfrom": reqfrom,
            "return_url": "http://msdt.cn/",
            "total_fee": int(total_fee),
            "client": "app",
            "show_url": "http://msdt.cn/",
            "ext": ext,
            "req_order_id": order_id,
            "order_data": ext_data,
            "addtime": datetime.datetime.now()
        }
        self.payorder_id = self.__conn.insert(the_order)
        the_order['_id'] = self.payorder_id
        self.payorder = the_order

    def link_order(self, order_id,dingjin=True):
        if self.payorder != {}:
            raise Exception('payOrder already linked!')
        order_data = self.__order_conn.find_one({'_id': order_id})

        yingfu = 0
        if dingjin:
            dis_amounts = 0.0
            for dis in order_data['dis_message']:
                dis_amounts += dis['dis_amount']
            yingfu = round(float(order_data['total'] - dis_amounts) * 0.1,2)
        else:
            yingfu = order_data['total'] - order_data['deposit']
        the_data = dict(
            subject='美食地图饭店订单' + order_id,
            body='',
            reqfrom='MSDT_order_app',
            total_fee=int(yingfu) * 100,
            order_id=order_data['_id'],
            ext_data={
                'restaurant_id': order_data['restaurant_id'],
                'webuser_id': order_data['webuser_id'],
                'total': order_data['total'],
                'deposit': order_data['deposit'],
                'username': order_data['username'],
                'room_id': order_data['room_id'],
                'preset_time': order_data['preset_time'],
                'demand': order_data['demand']
            }
        )
        self.__new_order(**the_data)
        return self.payorder
    def link_group(self, group_id):
        if self.payorder != {}:
            raise Exception('payOrder already linked!')
        group_data = self.__group_order_conn.find_one({'_id': group_id})
        infos = {}
        for n in group_data.keys():
            if isinstance(group_data[n], unicode) or isinstance(group_data[n], int):
                infos[n] = group_data[n]
        the_data = dict(
            subject='美食地图开团请客' + group_data['invite_code'],
            body='',
            reqfrom='MSDT_groupinvite_app',
            total_fee=str(int(MongoHelp('qingke').find_one({'_id': group_data['group_id']})['zj']) * 100),
            order_id=group_data['_id'],
            ext_data=infos
        )
        self.__new_order(**the_data)

    def req_pay(self, service='alipay'):
        if service not in ['alipay', 'wxpay']:
            raise Exception('Service must in [alipay] or [wxpay]')
        if self.payorder == {}:
            raise Exception('payOrder need linked!')
        from PaymentNG import Payment as PNG
        if service == 'alipay':
            return PNG().ORDER().new_alipay(**self.payorder)
        elif service == 'wxpay':
            return PNG().ORDER().new_wxpay(**self.payorder)

    pass


if __name__ == '__main__':
    pass
    # print PayOrder().link_order('573153c4e0fdb78f29b42826')
    print PayOrder('57ecb5f0fb98a411d0a03c0c').payorder['subject']
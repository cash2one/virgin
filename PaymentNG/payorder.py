# coding=utf-8

__author__ = 'dolacmeo'
__doc__ = '发起支付请求'

import sys
reload(sys)
sys.setdefaultencoding('utf8')
class PayOrder:
    def __init__(self, req_class):
        self.req = req_class
        pass

    def new_alipay(self, orderid, subject, body, reqfrom,  return_url, total_fee, client='web', show_url=None, ext=None, **unless):
        print 'new alipay'
        new_data = {
            'service': 'alipay',
            'OrderID': str(orderid),
            'subject': str(subject),
            'body': str(body),
            'reqfrom': str(reqfrom),
            'client': str(client),
            'return_url': str(return_url),
            'total_fee': total_fee
        }
        if show_url:
            new_data['show_url'] = str(show_url)
        if ext:
            new_data['ext'] = str(ext)
        return self.req.res('new_order', '', new_data).json()

    def new_wxpay(self, orderid, subject, body, reqfrom, total_fee, client='web', show_url=None, ext=None, **unless):
        print subject
        new_data = {
            'service': 'wechatpay',
            'OrderID': str(orderid),
            'subject': str(subject),
            'body': str(body),
            'reqfrom': str(reqfrom),
            'client': str(client),
            'return_url': 'http://###',
            'total_fee': total_fee
        }
        if show_url:
            new_data['show_url'] = str(show_url)
        if ext:
            new_data['ext'] = str(ext)
        return self.req.res('new_order', '', new_data).json()

    pass


if __name__ == '__main__':
    pass

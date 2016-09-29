# coding=utf-8
import requests

__author__ = 'dolacmeo'
__doc__ = 'HTTP请求'


class HttpReq:
    def __init__(self, base_url, ver='v1'):
        self.input_url = base_url
        self.base_url = base_url + '/api/' + ver
        pass

    def __is_ready(self):
        if self.input_url:
            return True
        else:
            raise Exception('Need Setting BASEURL, use Setting.url(NETGATE_URL)')

    def __make_fuc_url(self, fuc, the_id=''):
        # 发起新支付订单
        if fuc == 'new_order':
            return 'POST', self.base_url + '/payment/'
        # 根据订单id查询订单信息
        elif fuc == 'order_info':
            return 'GET', self.base_url + '/order/' + the_id
        # 根据流水id查询订单信息
        elif fuc == 'payment_info':
            return 'GET', self.base_url + '/payment/' + the_id
        # 获取退款单列表
        elif fuc == 'refund_list':
            return 'GET', self.base_url + '/refund/'
        # 发起新退款单
        elif fuc == 'new_refund':
            return 'POST', self.base_url + '/refund/'
        # 根据退款单id获取退款信息
        elif fuc == 'refund_info':
            return 'GET', self.base_url + '/refund/' + the_id
        # 提供退款单id审核此单
        elif fuc == 'refund_check':
            return 'POST', self.base_url + '/refund/' + the_id
        # 获取已审核通过的支付宝批量退款链接
        elif fuc == 'refund_alipay':
            return 'GET', self.base_url + '/refund/alipay/'
        # 对网关发起微信批量退款请求 将会处理已经通过申请的订单
        elif fuc == 'refund_wxpay':
            return 'GET', self.base_url + '/refund/wechatpay/'
        # 获取批量付款单信息
        elif fuc == 'get_batchpay':
            return 'GET', self.base_url + '/batchpay/'
        # 发起新的批量付款请求
        elif fuc == 'new_batchpay':
            return 'POST', self.base_url + '/batchpay/alipay'
        # 其他方法会报错
        else:
            print 'ERROR fuc'
            return 'GET', self.base_url

    def res(self, fuc, the_id='', req_data=None):
        self.__is_ready()
        method, http_url = self.__make_fuc_url(fuc, the_id)
        # print method, http_url
        if method == 'GET':
            return requests.get(http_url, req_data)
        elif method == 'POST':
            return requests.post(http_url, req_data)
        elif method == 'PUT':
            return requests.put(http_url, req_data)
        elif method == 'DELETE':
            return requests.delete(http_url)
        else:
            return None

    pass

if __name__ == '__main__':
    pass

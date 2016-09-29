# coding=utf-8
from http_fuc import HttpReq as req
from dataview import AllData
from payorder import PayOrder
from refund import Refund
from batchpay import BatchPay
from tool import Tools

__author__ = 'dolacmeo'
__doc__ = '整合支付接口'


class Payment:
    def __init__(self, BASEURL=None):
        self.BASEURL = BASEURL
        if not self.BASEURL:
            self.BASEURL = 'http://125.211.222.237:11036'
        pass

    def DATA(self):
        return AllData(req(self.BASEURL))

    def ORDER(self):
        return PayOrder(req(self.BASEURL))

    def REFUND(self):
        return Refund(req(self.BASEURL))

    def BATCHPAY(self):
        return BatchPay(req(self.BASEURL))

    def Tools(self):
        return Tools


if __name__ == '__main__':
    pass

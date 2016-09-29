# coding=utf-8

__author__ = 'dolacmeo'
__doc__ = '数据库查询'


class AllData:
    def __init__(self, req_class):
        self.req = req_class
        pass

    def orderid(self, orderid):
        # 根据订单ID查询详情
        return self.req.res('order_info', orderid).json()

    def paymentid(self, paymentid):
        # 根据支付流水ID查询详情
        return self.req.res('payment_info', paymentid).json()

    def refundid(self, refundid):
        # 根据退款id查询详情
        return self.req.res('refund_info', refundid).json()

    def refund_list(self, status='all', in_date='all', service='all'):
        # 获取退款申请列表
        if status not in ['IN_QUEUE', 'REFER', 'APPROVE', 'REFUNDED', 'all']:
            raise
        if in_date not in ['today', 'week', 'month', 'year', 'all']:
            raise
        if service not in ['alipay', 'wechatpay', 'all']:
            raise
        return self.req.res('refund_list', '', {
            'status': status, 'in_date': in_date, 'service': service
        }).json()

    def batchpay_list(self, time_range='all', page=0, limit=10):
        # 获取批量付款列表
        if time_range not in ['today', 'week', 'month', 'year', 'all']:
            raise
        return self.req.res('get_batchpay', '', {
            'time_range': time_range, 'limit': limit, 'page': page
        }).json()

    pass


if __name__ == '__main__':
    pass

# coding=utf-8

__author__ = 'dolacmeo'
__doc__ = '批量退款'


class Refund:
    def __init__(self, req_class):
        self.req = req_class
        pass

    def new(self, orderid, reqfrom, operator, remark, refund_fee, ext=None):
        # 发起新退款请求
        ask_order = {
            'OrderID': orderid,
            'reqfrom': reqfrom,
            'operator': operator,
            'remark': remark,
            'refund_fee': refund_fee,
        }
        if ext is not None:
            ask_order['ext'] = ext
        return self.req.res('new_refund', '', ask_order).json()

    def check(self, req_no, check_pass=True):
        # 提供退款单号 审核退款单
        return self.req.res('refund_check', req_no, {
            'check_pass': 'T' if check_pass else 'F'
        }).json()

    def ask_alipay(self, time_range='all'):
        # 获取支付宝批量退款链接 再进行下一步操作(必须使用IE浏览器)
        if time_range not in ['today', 'week', 'month', 'year', 'all']:
            raise
        return self.req.res('refund_alipay', '', {'time_range': time_range}).text()

    def ask_wxpay(self, time_range='all'):
        # 发起微信批量退款 最终返回批量操作结果
        if time_range not in ['today', 'week', 'month', 'year', 'all']:
            raise
        return self.req.res('refund_wxpay', '', {'time_range': time_range}).json()

    pass


if __name__ == '__main__':
    pass

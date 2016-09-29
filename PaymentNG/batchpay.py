# coding=utf-8

__author__ = 'dolacmeo'
__doc__ = '批量付款 仅支持支付宝'


class BatchPay:
    def __init__(self, req_class):
        self.req = req_class
        pass

    @staticmethod
    def __pay_data(data):
        the_data = []
        if isinstance(data, list):
            for n in data:
                the_data.append('^'.join([n['ali_account'], n['real_name'], n['fee'], n['remark']]))
            return '#'.join(the_data)
        else:
            raise Exception('INPUT DATA IS NOT LIST')

    def new_alipay(self, reqform, reason, operator, admin, data, ext=None):
        batchpay_data = {
            'reqform': str(reqform),
            'reason': str(reason),
            'operator': str(operator),
            'admin': str(admin),
            'data': self.__pay_data(data)
        }
        if ext is not None:
            batchpay_data['ext'] = ext
        return self.req.res('new_batchpay', '', batchpay_data)

    pass


if __name__ == '__main__':
    pass

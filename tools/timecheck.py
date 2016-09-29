# coding=utf-8
import datetime
from connect import conn
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class TimeCheck():
    def __init__(self, status= None, source=None, timeout=None):
        self.list = None
        self.mongo = conn.mongo_conn().order
        self.data = self._order_check(status= status, source=source, timeout=timeout)
        pass
    #待安置status[0,2] source[2]，待付款status[1] source[2]
    def _order_check(self, status= None, source=None, timeout=None):
        pass
        list = []
        item = self.mongo.find({"status":{"$in":status},"source":{"$in":source}})
        for i in item:
            if datetime.datetime.now()-datetime.timedelta(seconds = timeout * 60) > i['add_time']:
                list.append(i['_id'])
                print i['status']
        self.list = list
        # print list
        return self.list
    #待付款超时传6-用户退单，待安置超时传7商家退单
    def update_order(self, status=None):
        try:
            print self.list
            self.mongo.update({"_id":{"$in":self.list}},{"$set":{"status":status,"add_time":datetime.datetime.now()}},False,True)
            return True
        except Exception,e:
            print e
            return False
if __name__ == '__main__':
    pass
    # TimeCheck(status= [0,2], source=[2], timeout=45).update_order(7)
    # TimeCheck(status= [1], source=[2], timeout=45).update_order(6)
    # TimeCheck(status= [0,2], source=[2], timeout=45)
    # TimeCheck(status= [1], source=[2], timeout=45)



















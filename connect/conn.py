# coding=utf-8
from flask.ext.pymongo import MongoClient
# import redis
_author_ = 'hcy'

conn = 'mongodb://FoodMap32loK22Nk3oO_adm9n:UK#45JEIksiJEwi(209Y*nOwm@'
# ip_port0 = '125.211.222.237:27638'
ip_port0 = '192.168.22.101:27638'
auth = '/db_foodmap?authmechanism=SCRAM-SHA-1'
db_name = 'db_foodmap'


def mongo_conn():
    client = MongoClient(conn + ip_port0 + auth)
    db = client[db_name]
    return db


conn_user = 'mongodb://UserCenter_admin:UserCenter_admin_(*)@'
# ip_port0_user='125.211.222.237:27638'
ip_port0_user = '192.168.22.101:27638'
auth_user = '/db_UserCenter?authmechanism=SCRAM-SHA-1'
db_name_user = 'db_UserCenter'

imageIP = 'http://125.211.222.237:17937/'

def mongo_conn_user():
    client_user = MongoClient(conn_user + ip_port0_user + auth_user)
    db = client_user[db_name_user]
    return db


if __name__ == '__main__':
    pass

#--coding:utf-8--#
_author_='hcy'
from flask.ext.pymongo import MongoClient
import  redis

conn = 'mongodb://FoodMap32loK22Nk3oO_adm9n:UK#45JEIksiJEwi(209Y*nOwm@'
ip_port0 = '125.211.222.237:27638'
auth = '/db_foodmap?authmechanism=SCRAM-SHA-1'
db_name = 'db_foodmap'

def mongo_conn():
    client = MongoClient(conn + ip_port0 + auth)
    db = client[db_name]
    return db
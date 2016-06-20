# coding=utf-8
__author__ = 'hcy'
import  sys
reload(sys)
sys.setdefaultencoding('utf8')

mgs_template ={
    "sj_1":{ #推送原因：用户订座提示
        "title":"您有一条订座消息，快去查看吧",
        "text":
        "联系人：%(name)s\n联系电话：%(phone)s\n\
        用餐时间：%(date)s\n用餐人数：%(num)s\n\
        包房/大厅：%(isroom)s\n要求:%(need)s\n"
    },
    "sj_2":{ #推送原因：用户点菜提示
        "title":"您有一条点菜消息，快去查看吧",
        "text":
        "联系人：%(name)s\n联系电话：%(phone)s\n用餐时间：%(date)s\n用餐人数：%(num)s\n包房/大厅：%(isroom)s\n要求:%(need)s\n菜单:%(dishs)s\n"
    },
    "sj_3":{ #推送原因：开团请客活动名额被抢
        "title":"您发起的开团请客活动被抢了",
        "text":"抢单人:%(name)s\n 内容:%(num)s人成团共享%(money)s优惠价\n抢单时间：%(date)s\n付款时间：%(paydate)s\n联系电话：%(phone)s\n剩余分数:%(copies)s\n"
    },
    "sj_4":{ #推送原因：店粉儿抢优惠被抢
        "title":"您发布的店粉儿抢优惠被抢了",
        "text":"抢单人:%(name)s\n内容:%(content)s\n抢单时间:%(data)s\n联系电话:%(phone)s\n剩余名额:%(copies)s\n"
    },
    "sj_5":{ #推送原因：订座时间提前提醒
        "title":"***（包房名）包房***（时间）有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n"
    },
    "sj_6":{
        "title":"%(roomsname)s\n包房 %(data)s 有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n"
    },
    "sj_7":{
        "title":"%(roomsname)s\n包房 %(data)s 有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n"
    }
}

# def send(a):
#


if __name__ == '__main__':
  print mgs_template["sj_1"]["title"]
  print (mgs_template["sj_1"]["text"]%{"name":"wangxianheng","phone":"185246121","date":"2016年","num":"4","isroom":"大厅","need":""})

# coding=utf-8
__author__ = 'hcy'
import  sys
reload(sys)
sys.setdefaultencoding('utf8')

page_template={
    "1":"详见商家版APP  1-1-1",
    "2":"详见商家版APP  1-1-2",
    "3":"详见用户版APP 2-4-2",
    "4":"详见用户版APP 2-4-3",
    "5":"消息细缆"
}


mgs_template ={
    "sj_1":{ #推送原因：用户订座提示
        "title":"您有一条订座消息，快去查看吧",
        "text":"联系人：%(name)s\n联系电话：%(phone)s\n用餐时间：%(date)s\n用餐人数：%(num)s\n包房/大厅：%(isroom)s\n要求:%(need)s\n",
        "goto":"1",
        "is_push":True,
        "channel":"订单"
    },
    "sj_2":{ #推送原因：用户点菜提示
        "title":"您有一条点菜消息，快去查看吧",
        "text":"联系人：%(name)s\n联系电话：%(phone)s\n用餐时间：%(date)s\n用餐人数：%(num)s\n包房/大厅：%(isroom)s\n要求:%(need)s\n菜单:%(dishs)s\n",
        "goto":"2",
        "is_push":True,
        "channel":"订单"
    },
    "sj_3":{ #推送原因：开团请客活动名额被抢
        "title":"您发起的开团请客活动被抢了",
        "text":"抢单人:%(name)s\n 内容:%(num)s人成团共享%(money)s优惠价\n抢单时间：%(date)s\n付款时间：%(paydate)s\n联系电话：%(phone)s\n剩余分数:%(copies)s\n",
        "goto":"5",
        "is_push":True,
        "channel":"开团请客"
    },
    "sj_4":{ #推送原因：店粉儿抢优惠被抢
        "title":"您发布的店粉儿抢优惠被抢了",
        "text":"抢单人:%(name)s\n内容:%(content)s\n抢单时间:%(data)s\n联系电话:%(phone)s\n剩余名额:%(copies)s\n",
        "goto":"5",
        "is_push":True,
        "channel":"抢优惠"
    },
    "sj_5":{ #推送原因：订座时间提前提醒  备注：比约定的吃饭时间1小时发送  系统发
        "title":"***（包房名）包房***（时间）有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
    "sj_6":{ #推送原因：点菜时间提醒 备注：比约定的吃饭时间1小时发送  系统发
        "title":"%(roomsname)s\n包房 %(data)s 有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
    "sj_7":{ #推送原因：优惠/活动过期/被抢光  用户抢操作
        "title":"%(roomsname)s\n包房 %(data)s 有预定，请提前准备",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
    "yh_1":{ #推送原因：开团请客有人应邀   用户--用户   用户参加优惠时
        "title":"有人加入了您的 %(redname)s 的开团请客活动，快去看看吧。",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n",
        "goto":"3",
        "is_push":True,
        "channel":"开团请客"
    },
    "yh_2":{ #推送原因：开团请客该付款
        "title":"您的 %(redname)s 饭店开团请客活动该付款了，快去看看吧。",
        "text":"联系人:%(name)s\n联系电话:%(phone)s\n",
        "goto":"3",
        "is_push":True,
        "channel":"开团请客"
    },
    "yh_3":{ #推送原因：订单被确认
        "title":"您的订单已被安排，点击查看详细内容，祝您用餐愉快。",
        "text":"您好：尊敬的%(name)s,%(redname)s%(data)s为您预留了%(roomname)s房间，菜单：%(dishs)s，地址：%(address)s，电话：%(phone)s,祝您用餐愉快",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
    "yh_4":{ #推送原因：订座、点菜 提前提示
        "title":"您预订的 %(renname)s 饭店已为您安排好了，欢迎您 %(data)s 前来就餐",
        "text":"您预订的 %(renname)s 饭店已为您安排好了，欢迎您 %(data)s 前来就餐\n联系电话：%(data)",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
    "yh_5":{ #推送原因：优惠到期提醒  备注：优惠过期提前一天发送
        "title":"您%(roomsname)s\n店铺的优惠快到期了，快去消费吧。",
        "text":"店铺名称:%(name)s\n有效期:%(data)s\n优惠:%(youhui)s\n饭店电话:%(phone)s\n",
        "con1":"%(yuan)s元 代金券",
        "con2":"%(zhekou)s折 折扣券",
        "con3":"%(shiwu)s实物券",
        "con4":"%(yuan)s元%(people)s人开团请客活动",
        "goto":"5",
        "is_push":True,
        "channel":"优惠"
    },
    "yh_6":{ #推送原因：订单被拒绝
        "title":"很遗憾，店铺无法为你安排就餐。",
        "text":"回执时间：%(data)s ,处理结果：很遗憾，店铺无法为你安排就餐",
        "goto":"5",
        "is_push":True,
        "channel":"订单"
    },
}

# def send(a):
#


if __name__ == '__main__':
  print mgs_template["sj_1"]["title"]
  print (mgs_template["sj_1"]["text"]%{"name":"wangxianheng","phone":"185246121","date":"2016年","num":"4","isroom":"大厅","need":""})

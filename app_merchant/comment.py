# coding=utf-8
from bson import json_util
from flask import Blueprint, request, abort
import datetime
import time
import tools.tools as tool
from app_merchant import auto
__author__ = 'dolacmeo'

restaurant_comment = Blueprint('restaurant_comment', __name__, template_folder='templates')


@restaurant_comment.route('/fm/merchant/v1/comment/restaurant_comment_list/', methods=['POST'])
def restaurant_comment_list():
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):

            start = datetime.datetime(*time.strptime(request.form['start_time'], '%Y-%m-%d')[:6])
            end = datetime.datetime(*time.strptime(request.form['end_time'], '%Y-%m-%d')[:6]) + datetime.timedelta(days=1)
            try:
                from tools.db_comment import Comment
                m = {'restaurant_id': request.form['restaurant_id'], 'post_date': {"$gte": start, "$lte": end}}
                if 'stars' in request.form:
                    m['rating.total'] = request.form['stars']
                found = Comment().conn.find(m).skip(int(request.form['skip'])).limit(10)
                if found:
                    found = json_util.loads(json_util.dumps(found))
                    for n in found:
                        del n['dish_id']
                        del n['order_id']
                        n['_id'] = str(n['_id'])
                        n['post_date'] = n['post_date'].strftime('%Y年%m月%d日 %H:%M:%S')
                else:
                    found = []
                result = tool.return_json(0, "success", True, found)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            except Exception, e:
                print e
                result = tool.return_json(0, "field", False, e)
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            pass
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
    pass


@restaurant_comment.route('/fm/diners/v1/dishs/praiselist/', methods=['POST'])
def dishlikes():
    if request.method == 'POST':
        try:
            from tools.db_dishlikes import DishLikes
            if 'restaurant_id' in request.form:
                start = datetime.datetime(*time.strptime(request.form['start_time'], '%Y-%m-%d')[:6])
                end = datetime.datetime(*time.strptime(request.form['end_time'], '%Y-%m-%d')[:6]) + datetime.timedelta(days=1)
                f = {'restaurant_id': request.form['restaurant_id'], 'timestamp': {"$gte": start, "$lte": end}}
                found = DishLikes().shoplikes(f)
            elif 'user_id' in request.form:
                f = {'user_id': request.form['user_id']}
                found = DishLikes().findlikes(f)
            else:
                result = tool.return_json(0, "field", False, 'Request id Not Support')
                return json_util.dumps(result, ensure_ascii=False, indent=2)
            if found['success']:
                jwtmsg = auto.decodejwt(request.form["jwtstr"])
                result = tool.return_json(0, "success", jwtmsg, found['data'])
            else:
                result = tool.return_json(0, "field", False, found['error'])
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        except Exception, e:
            print e
            result = tool.return_json(0, "field", False, e)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        pass
    else:
        return abort(403)
    pass


@restaurant_comment.route('/fm/diners/v1/dishs/praise/', methods=['POST'])
def user_likes():
    if request.method == 'POST':
        for n in ['user_id', 'dish_id', 'restaurant_id', 'method']:
            if n not in request.form:
                return abort(406)
        try:
            from tools.db_dishlikes import DishLikes
            todo = {'user_id': request.form['user_id'],
                    'dish_id': request.form['dish_id'],
                    'restaurant_id': request.form['restaurant_id']}
            if request.form['method'] == 'like':
                handle = DishLikes().addlike(todo)
            elif request.form['method'] == 'dislike':
                handle = DishLikes().dislike(todo)
            else:
                return abort(403)
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            if handle['success']:
                result = tool.return_json(0, "success", jwtmsg, True)
            else:
                result = tool.return_json(0, "field", False, handle['error'])
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        except Exception, e:
            print e
            result = tool.return_json(0, "field", False, e)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)


if __name__ == '__main__':
    # start = datetime.datetime(*time.strptime('2016-01-01', '%Y-%m-%d')[:6])
    # end = datetime.datetime(*time.strptime('2016-06-01', '%Y-%m-%d')[:6]) + datetime.timedelta(days=1)
    # from tools.db_comment import Comment
    # mm = {'restaurant_id': '57329d530c1d9b2f4c85f8e5', 'post_date': {"$gte": start, "$lte": end}}
    # found = Comment().conn.find(mm).skip(1).limit(2)
    # print json_util.dumps(found, indent=2)
    # print len(json_util.loads(json_util.dumps(found)))
    pass

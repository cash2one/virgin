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
            else:
                found = []
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result = tool.return_json(0, "success", jwtmsg, found)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        except Exception, e:
            print e
            result = tool.return_json(0, "field", False, e)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        pass
    else:
        abort(403)
    pass


if __name__ == '__main__':
    # start = datetime.datetime(*time.strptime('2016-01-01', '%Y-%m-%d')[:6])
    # end = datetime.datetime(*time.strptime('2016-06-01', '%Y-%m-%d')[:6]) + datetime.timedelta(days=1)
    # from tools.db_comment import Comment
    # mm = {'restaurant_id': '57329d530c1d9b2f4c85f8e5', 'post_date': {"$gte": start, "$lte": end}}
    # found = Comment().conn.find(mm).skip(1).limit(2)
    # print json_util.dumps(found, indent=2)
    # print len(json_util.loads(json_util.dumps(found)))
    pass

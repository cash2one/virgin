# coding=utf-8
from datetime import datetime
import tools.tools as tool
from bson import json_util
from flask import Blueprint, render_template, request, abort, json
from tools.db_comment import Comment
from app_merchant import auto

__author__ = 'dolacmeo'

user_comment = Blueprint("user_comment", __name__, template_folder='templates')


def is_one(key, form):
    if key in form:
        return form[key]
    else:
        print 'No key %s in comment' % key
        return ''
    pass


@user_comment.route('/fm/diners/v1/comment/submit/', methods=['POST'])
def app_comment_submit():
    if request.method == 'POST':
        for n in ['restaurant_id', 'user_id', 'user_name', 'user_head', 'comment_text', 'comment_pic', 'rating_total',
                  'rating_taste', 'rating_env', 'rating_service']:
            if n not in request.form:
                return abort(406)
        data = {
            'restaurant_id': is_one('restaurant_id', request.form),
            'dish_id': is_one('dish_id', request.form),
            'order_id': is_one('order_id', request.form),
            'user_id': is_one('user_id', request.form),
            'user_info': {'user_name': is_one('user_name', request.form),
                          'user_head': is_one('user_head', request.form)},
            'post_date': datetime.now(),
            'rating': {'total': is_one('rating_total', request.form),
                       'taste': is_one('rating_taste', request.form),
                       'env': is_one('rating_env', request.form),
                       'service': is_one('rating_service', request.form)},
            'comment_text': is_one('comment_text', request.form),
            'comment_pic': json.loads(is_one('comment_pic', request.form))
        }
        if Comment().add(data):
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result = tool.return_json(0, "success", jwtmsg, '')
            return json_util.dumps(result, ensure_ascii=False, indent=2)
        else:
            result = tool.return_json(0, "field", False, None)
            return json_util.dumps(result, ensure_ascii=False, indent=2)
    else:
        return abort(403)
    pass


if __name__ == '__main__':
    pass

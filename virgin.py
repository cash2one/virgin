# --coding:utf-8--#
# import jwt
from flask import Flask, make_response, jsonify
from werkzeug.security import safe_str_cmp

from app_merchant.coupons import coupons_api
from app_merchant.me import me_api
from app_merchant.message import message_api
from app_user.coupons import coupons_user_api
from app_user.index import index_api
from app_user.login import login_user_api
from app_user.me import me_user_api
from app_user.restaurant import restaurant_user_api
from tools.error_warning import error_api
from test.test import test_api
from test.first_demo import firstdemo_api
from test.autotest import autotest_api
from app_merchant.order import order_api
from app_merchant.restaurant import restaurant_api
from app_merchant.members import members_api
from app_merchant.other import other_api
from app_merchant.auto import auto_api
from app_user.user import user_api
from app_user.comment import user_comment
from app_merchant.comment import restaurant_comment
from app_user.groupinvite import group_invite
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)
app.config['DEBUG'] = True

app.register_blueprint(error_api)
app.register_blueprint(test_api)
app.register_blueprint(firstdemo_api)
app.register_blueprint(autotest_api)
app.register_blueprint(order_api)
app.register_blueprint(restaurant_api)
app.register_blueprint(members_api)
app.register_blueprint(other_api)
app.register_blueprint(auto_api)
app.register_blueprint(user_api)
app.register_blueprint(user_comment)
app.register_blueprint(restaurant_comment)
app.register_blueprint(coupons_api)
app.register_blueprint(me_api)
app.register_blueprint(index_api)
app.register_blueprint(restaurant_user_api)
app.register_blueprint(message_api)
app.register_blueprint(group_invite)
app.register_blueprint(login_user_api)
app.register_blueprint(me_user_api)
app.register_blueprint(coupons_user_api)


@app.route('/protected', methods=['POST'])
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run()

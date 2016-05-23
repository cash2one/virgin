# --coding:utf-8--#
# import jwt
from flask import Flask, make_response, jsonify
from werkzeug.security import safe_str_cmp

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

app = Flask(__name__)
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


@app.route('/protected', methods=['POST'])
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run()

#--coding:utf-8--#
# import jwt
from flask import Flask,make_response,jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp


from tools.error_warning import error_api
from test.test import test_api
from test.first_demo import firstdemo_api
from test.autotest import autotest_api
from app_merchant.order import order_api




app = Flask(__name__)
app.config['DEBUG'] = True

app.register_blueprint(error_api)
app.register_blueprint(test_api)
app.register_blueprint(firstdemo_api)
app.register_blueprint(autotest_api)
app.register_blueprint(order_api)



@app.route('/protected', methods=['POST'])
@jwt_required()
def protected():
    return '%s' % current_identity


@app.errorhandler(404)
def not_found(error):
    return  make_response(jsonify({'error':'Not found'}),404)


if __name__ == '__main__':
    app.run()

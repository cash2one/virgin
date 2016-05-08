#--coding:utf-8--#
# import jwt
from flask import Flask,make_response,jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp


from tools.error_warning import error_api
from test.test import test_api
from test.first_demo import firstdemo_api
from test.autotest import autotest_api


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    User(1, 'user1', 'abcxyz'),
    User(2, 'user2', 'abcxyz'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

app.register_blueprint(error_api)
app.register_blueprint(test_api)
app.register_blueprint(firstdemo_api)
app.register_blueprint(autotest_api)





jwt = JWT(app, authenticate, identity)

@app.route('/protected', methods=['POST'])
@jwt_required()
def protected():
    return '%s' % current_identity


@app.errorhandler(404)
def not_found(error):
    return  make_response(jsonify({'error':'Not found'}),404)


if __name__ == '__main__':
    app.run()

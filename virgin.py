#--coding:utf-8--#
from flask import Flask,make_response,jsonify

from tools.error_warning import error_api
from test.test import test_api
from test.first_demo import firstdemo_api

app = Flask(__name__)
app.config['DEBUG'] = True

app.register_blueprint(error_api)
app.register_blueprint(test_api)
app.register_blueprint(firstdemo_api)


@app.errorhandler(404)
def not_found(error):
    return  make_response(jsonify({'error':'Not found'}),404)


if __name__ == '__main__':
    app.run()

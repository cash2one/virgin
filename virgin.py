#--coding:utf-8--#
from flask import Flask

from tools.error_warning import error_api
from test.test import test_api
from test.first_demo import firstdemo_api

app = Flask(__name__)
app.config['DEBUG'] = True

app.register_blueprint(error_api)
app.register_blueprint(test_api)
app.register_blueprint(firstdemo_api)

if __name__ == '__main__':
    app.run()

#--coding:utf-8--#
from flask import Flask

from tools.error_warning import error_api
from test.test import test_api


app = Flask(__name__)
app.config['DEBUG'] = True

error_api.register_blueprint(error_api)
error_api.register_blueprint(test_api)

if __name__ == '__main__':
    app.run()

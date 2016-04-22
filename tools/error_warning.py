#--coding:utf-8--#
_author_='hcy'
from flask import make_response,Blueprint,jsonify

error_api = Blueprint('error_api', __name__)

@error_api.errorhandler(404)
def not_found(error):
    return  make_response(jsonify({'error':'Not found'}),404)


import os

from flask import Blueprint, jsonify


url_prefix = os.getenv('URL_PREFIX')
blueprint = Blueprint('health', __name__, url_prefix=url_prefix)

@blueprint.route('/health')
def health():
    return jsonify(status=200, message='OK!')

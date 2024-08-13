import awsgi

from common import safe_serialize
from flask import Flask

from views.health import blueprint as health_api
from views.chatbot import blueprint as chatbot_api


def lambda_handler(event, context):
    print('DEBUG - EVENT - {}'.format(safe_serialize(event)))

    app = Flask(__name__)
    app.register_blueprint(health_api)
    app.register_blueprint(chatbot_api)

    return awsgi.response(app, event, context)

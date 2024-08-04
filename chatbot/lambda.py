import awsgi
import json

from flask import Flask, g

from views.health import blueprint as health_api
from views.chatbot import blueprint as chatbot_api


def lambda_handler(event, context):
    print('DEBUG - EVENT - {}'.format(json.dumps(event)))

    app = Flask(__name__)
    app.register_blueprint(health_api)
    app.register_blueprint(chatbot_api)

    return awsgi.response(app, event, context)

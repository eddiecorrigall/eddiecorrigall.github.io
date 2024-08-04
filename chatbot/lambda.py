import awsgi
import json

from flask import Flask, g

from dao.messages import MessagesDAO
from views.health import blueprint as health_api
from views.chatbot import blueprint as chatbot_api


def handle_provisioning(dao) -> dict:
    is_ready, error = dao.provision()
    if not is_ready:
        print('ERROR: {}'.format(error))
        return {
            'statusCode': 503,
            'body': 'Service unavailable'
        }

def lambda_handler(event, context):
    print('DEBUG - EVENT - {}'.format(json.dumps(event)))

    messages_dao = MessagesDAO()
    response = handle_provisioning(messages_dao)
    if response:
        return response
    
    app = Flask(__name__)
    app.register_blueprint(health_api)
    app.register_blueprint(chatbot_api)
    with app.app_context():
        g.messages_dao = messages_dao

    return awsgi.response(app, event, context)

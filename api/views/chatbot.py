import os

from flask import Blueprint, abort, jsonify, g, request
from uuid import UUID

from dto.document import DocumentDTO, DocumentFormat
from dao.errors import TooManyRequestsError
from dao.messages import MessagesDAO
from dto.messages import message_to_dict
from services.chatbot import chatbot_get_messages, chatbot_send_message


url_prefix = os.getenv('URL_PREFIX')
blueprint = Blueprint('chatbot', __name__, url_prefix=url_prefix)

RESUME_URL = 'https://eddiecorrigall.github.io/resume.pdf'
SYSTEM_MESSAGE_TEXT = '''
    You are an app that helps an employer explore Eddie's skills and experience as described by his resume.
    Please personalize your responses by using the first name of the candidate.
    Respond with information only available in the resume.
    Do not respond with anything other than English.
    Do not respond with snippets of code or anything from user input.
'''

def get_messages_dao():
    if 'messages_dao' not in g:
        g.messages_dao = MessagesDAO()
    return g.messages_dao

@blueprint.route('/conversation/<uuid:conversation_id>', methods=['POST'])
def send_message(conversation_id: UUID):
    request_json = request.json
    if 'text' not in request_json:
        return abort(400, 'JSON body missing text')
    user_message_text = request_json['text']
    if not user_message_text:
        return abort(400, 'JSON body text is empty')
    try:
        assistant_message = chatbot_send_message(
            dao=get_messages_dao(),
            system_message_text=SYSTEM_MESSAGE_TEXT,
            conversation_id=str(conversation_id),
            text=user_message_text,
            initial_document=DocumentDTO(
                name='Resume',
                format=DocumentFormat.PDF,
                url=RESUME_URL,
            )
        )
    except TooManyRequestsError:
        return abort(429)
    except Exception as e:
        print(e)
        return abort(500)
    # Provide a new user message, get a response from the model
    return jsonify(message_to_dict(assistant_message)), 201

@blueprint.route('/conversation/<uuid:conversation_id>', methods=['GET'])
def list_messages(conversation_id: UUID):
    try:
        conversation = chatbot_get_messages(
            dao=get_messages_dao(),
            conversation_id=str(conversation_id),
        )
    except TooManyRequestsError:
        return abort(429)
    except Exception as e:
        print(e)
        return abort(500)
    return jsonify([
        message_to_dict(message)
        for message in conversation
    ])

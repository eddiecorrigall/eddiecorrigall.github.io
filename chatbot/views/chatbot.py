import os

from datetime import datetime
from flask import Blueprint, abort, g, request

from dto.messages import MessageDTO, MessageRole
from services.chatbot import chatbot_send_message


url_prefix = os.getenv('URL_PREFIX')
blueprint = Blueprint('health', __name__, url_prefix=url_prefix)

@blueprint.route('/conversation/<int:conversation_id>', methods=['POST'])
def message(conversation_id):
    request_json = request.json
    if 'text' not in request_json:
        return abort(400, 'JSON body missing text')
    user_message_text = request_json['text']
    if not user_message_text:
        return abort(400, 'JSON body text is empty')
    user_message = MessageDTO(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        created_at=datetime.now(),
        text=user_message_text,
    )
    assistant_message = chatbot_send_message(
        dao=g.messages_dao,
        conversation_id=conversation_id,
        user_message=user_message,
    )
    # Provide a new user message, get a response from the model
    return str(assistant_message), 201

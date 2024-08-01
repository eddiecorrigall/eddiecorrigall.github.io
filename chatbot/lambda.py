import awsgi
import boto3
import json

from datetime import datetime

from flask import (
    Flask,
    jsonify,
    request,
)


app = Flask(__name__)
bedrock = boto3.client(service_name='bedrock-runtime')

SYSTEM_MESSAGE = (
    'You are an app that creates playlists for a radio station that plays rock and pop music.'
    'Only return song names and the artist.'
)

class Message:
    @classmethod
    def from_user(cls, date, text):
        return cls(date, True, text)

    @classmethod
    def from_assistant(cls, date, text):
        return cls('assistant', date, text)

    @classmethod
    def from_system(cls, date, text):
        return cls('user', date, text)

    def __init__(self, role, date, text):
        self.role = role
        self.date = date
        self.text = text

    def to_bedrock(self):
        return json.dumps({
            # user — The human that is sending messages to the model
            # assistant — The model that is sending messages back to the human user
            'role': self.role,
            'content': [{'text': self.text}]
        })

    def __str__(self):
        return json.dumps({
            'is_user': self.is_user,
            'date': self.date.isoformat(),
            'text': self.text,
        })

def load_conversation(conversation_id):
    # TODO: load...
    return []

def save_message(conversation_id, message):
    conversation = load_conversation(conversation_id=conversation_id)
    conversation.append(message)
    # TODO: persist...
    return conversation

def ask_chatbot(conversation_id, latest_user_message):
    # https://aws.amazon.com/blogs/aws/announcing-llama-3-1-405b-70b-and-8b-models-from-meta-in-amazon-bedrock/
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
    conversation = save_message(conversation_id=conversation_id, message=latest_user_message)
    # Convert to bedrock conversation...
    bedrock_conversation = sorted(
        conversation,
        key=lambda message: message.date,
    )
    bedrock_conversation = map(lambda message: message.to_bedrock())
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
    response = bedrock.converse(
        # modelId='meta.llama3-1-405b-instruct-v1:0',
        modelId='meta.llama3-70b-instruct-v1:0',
        # modelId='meta.llama3-8b-instruct-v1:0',
        system=[{'text': SYSTEM_MESSAGE}],
        messages=bedrock_conversation,
        inferenceConfig={'maxTokens': 512, 'temperature': 0.5, 'topP': 0.9},
    )
    response_text = response['output']['message']['content'][0]['text']
    latest_assistant_message = Message.from_assistant(date=datetime.now(), text=response_text)
    conversation = save_message(conversation_id=conversation_id, message=latest_assistant_message)
    return latest_assistant_message

def lambda_handler(event, context):
    print('DEBUG - EVENT: ' + json.dumps(event))
    return awsgi.response(app, event, context)

PREFIX = '/live/chatbot'

@app.route(PREFIX + '/health')
def health():
    return jsonify(status=200, message='OK!')

@app.route(PREFIX + '/conversation/<int:conversation_id>', methods=['GET', 'POST'])
def message(conversation_id):
    if request.method == 'POST':
        request_json = request.json()
        user_message = Message.from_user(
            date=datetime.now(),
            text=request_json['text'],
        )
        assistant_message = ask_chatbot(conversation_id=conversation_id, latest_user_message=user_message)
        # Provide a new user message, get a response from the model
        return jsonify(assistant_message), 201
    else:
        # Get the entire conversation
        return jsonify('OK!'), 200

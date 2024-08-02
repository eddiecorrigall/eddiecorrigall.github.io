import awsgi
import boto3
import json
import os

from datetime import datetime

from flask import (
    Flask,
    abort,
    jsonify,
    request,
)


app = Flask(__name__)
bedrock = boto3.client(service_name='bedrock-runtime')
dynamodb = boto3.resource(service_name='dynamodb')

MESSAGES_TABLE_NAME = "ChatbotMessages"

def hasMessagesTable():
    try:
        dynamodb.Table(MESSAGES_TABLE_NAME).table_status
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return False

def getMessagesTable():
    return dynamodb.Table(MESSAGES_TABLE_NAME)

def createMessagesTable():
    return dynamodb.create_table(
        TableName=MESSAGES_TABLE_NAME,
        AttributeDefinitions=[
            {
                'AttributeName': 'ConversationID',
                'AttributeType': 'S',
            },
            {
                'AttributeName': 'CreatedAt',
                'AttributeType': 'N',
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'ConversationID',
                'KeyType': 'HASH',
            },
            {
                'AttributeName': 'CreatedAt',
                'KeyType': 'RANGE',
            },
        ],
        BillingMode='PAY_PER_REQUEST',
        SSESpecification={
            'Enabled': True,
        },
        TableClass='STANDARD',
        DeletionProtectionEnabled=True,
    )

SYSTEM_MESSAGE = '''
    You are an app that creates playlists for a radio station that plays music.
    Response with at most 3 songs.
    Only return song names and the song artist.
'''

class Message:
    @classmethod
    def from_user(cls, date, text):
        return cls(True, date, text)

    @classmethod
    def from_assistant(cls, date, text):
        return cls(False, date, text)

    def __init__(self, is_user, date, text):
        self.is_user = is_user
        self.date = date
        self.text = text

    def to_bedrock(self):
        return {
            # user — The human that is sending messages to the model
            # assistant — The model that is sending messages back to the human user
            'role': 'user' if self.is_user else 'assistant',
            'content': [{'text': self.text}]
        }

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
    bedrock_conversation = list(conversation)
    bedrock_conversation = sorted(
        bedrock_conversation,
        key=lambda message: message.date,
    )
    bedrock_conversation = map(lambda message: message.to_bedrock(), bedrock_conversation)
    bedrock_conversation = list(bedrock_conversation)
    print('DEBUG - bedrock_conversation: ' + json.dumps(bedrock_conversation))
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
    print('DEBUG - EVENT - {}'.format(json.dumps(event)))

    if not hasMessagesTable():
        createMessagesTable()
        return {
            'statusCode': 503,
            'body': 'Service unavailable'
        }

    table = getMessagesTable()

    return awsgi.response(app, event, context)

PREFIX = '/live/chatbot'

@app.route(PREFIX + '/health')
def health():
    return jsonify(status=200, message='OK!')

@app.route(PREFIX + '/conversation/<int:conversation_id>', methods=['POST'])
def message(conversation_id):
    request_json = request.json
    if 'text' not in request_json:
        return abort(400, 'JSON body missing text')
    user_message_text = request_json['text']
    if not user_message_text:
        return abort(400, 'JSON body text is empty')
    user_message = Message.from_user(
        date=datetime.now(),
        text=user_message_text,
    )
    assistant_message = ask_chatbot(conversation_id=conversation_id, latest_user_message=user_message)
    # Provide a new user message, get a response from the model
    return str(assistant_message), 201

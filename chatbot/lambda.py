import awsgi
import boto3

from flask import (
    Flask,
    jsonify,
)


app = Flask(__name__)
bedrock = boto3.client(service_name='bedrock-runtime')

SYSTEM_MESSAGE = (
    "You are an app that creates playlists for a radio station that plays rock and pop music."
    "Only return song names and the artist."
)

def get_chatbot_response(messages):
    # https://aws.amazon.com/blogs/aws/announcing-llama-3-1-405b-70b-and-8b-models-from-meta-in-amazon-bedrock/
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
    conversation = []
    for message in messages:
        conversation.append({
            'role': 'user',
            'content': [{'text': message}],
        })
    response = bedrock.converse(
        # modelId='meta.llama3-1-405b-instruct-v1:0',
        modelId='meta.llama3-70b-instruct-v1:0',
        # modelId='meta.llama3-8b-instruct-v1:0',
        system=[{"text": SYSTEM_MESSAGE}],
        messages=conversation,
        inferenceConfig={'maxTokens': 512, 'temperature': 0.5, 'topP': 0.9},
    )
    response_text = response['output']['message']['content'][0]['text']
    return response_text

def lambda_handler(event, context):
    return awsgi.response(app, event, context)

PREFIX = 'chatbot'

@app.route(PREFIX + '/')
def home():
    return jsonify(status=200, message='HOME!')

@app.route(PREFIX + '/health')
def health():
    return jsonify(status=200, message='OK!')

@app.route(PREFIX + '/conversation/{id}/message')
def message():
    return jsonify(status=200, message='OK!')

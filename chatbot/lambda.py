import boto3
import traceback


bedrock = boto3.client(service_name='bedrock-runtime')

system_prompt = (
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
        system=[{"text": system_prompt}],
        messages=conversation,
        inferenceConfig={'maxTokens': 512, 'temperature': 0.5, 'topP': 0.9},
    )
    response_text = response["output"]["message"]["content"][0]["text"]
    return response_text

def lambda_handler(event, context):
    allow_origins = [
        'http://localhost:1313',
        'https://eddiecorrigall.github.io'
    ]
    messages = [
        'Create a list of 3 pop songs.'
    ]
    response = ''
    try:
        response = get_chatbot_response(messages)
    except Exception as e:
        return {
            'errorType': 'InternalServerError',
            'requestId': context.aws_request_id,
            'stackTrace': traceback.format_exc()
        }
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'plain/text',
            'Access-Control-Allow-Origin': '*', # ', '.join(allow_origins)
            'X-BOTO3-VERSION': boto3.__version__
        },
        'body': response
    }

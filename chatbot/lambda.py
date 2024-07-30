import boto3
import traceback


bedrock = boto3.client(service_name='bedrock-runtime')

def get_chatbot_response(request):
    # https://aws.amazon.com/blogs/aws/announcing-llama-3-1-405b-70b-and-8b-models-from-meta-in-amazon-bedrock/
    conversation = [
        {
            'role': 'system',
            'content': [{'text': 'You are a helpful assistant.'}]
        },
        {
            'role': 'user',
            'content': [{'text': request}],
        }
    ]
    response = bedrock.converse(
        modelId='meta.llama3-1-405b-instruct-v1:0',
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )
    response_text = response["output"]["message"]["content"][0]["text"]
    return response_text

def lambda_handler(event, context):
    allow_origins = [
        'http://localhost:1313',
        'https://eddiecorrigall.github.io'
    ]
    request = "Describe the purpose of a 'hello world' program in one line."
    response = ''
    try:
        response = get_chatbot_response(request)
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

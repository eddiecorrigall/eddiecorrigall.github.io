import boto3


def handler(event, context):
    allow_origins = [
        'http://localhost:1313',
        'https://eddiecorrigall.github.io'
    ]
    return {
        'statusCode' : 200,
        'headers': {
            'Content-Type': 'plain/text',
            'Access-Control-Allow-Origin': '*' # ', '.join(allow_origins)
        },
        'body': 'Hello World'
    }

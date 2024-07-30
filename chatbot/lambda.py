import boto3


def handler(event, context):
    cors_allow_origins = [
        'http://localhost:1313',
        'https://eddiecorrigall.github.io'
    ]
    return {
        'statusCode' : 200,
        'headers': {
            'Access-Control-Allow-Origin': ','.join(cors_allow_origins)
        },
        'body': 'Hello World'
    }

import boto3


def handler(event, context):
    return {
        'statusCode' : 200,
        'body': 'Hello World'
    }

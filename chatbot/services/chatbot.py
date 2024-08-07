import boto3
import json
import requests

from datetime import datetime

from dao.messages import MessagesDAO
from dto.messages import MessageDTO, MessageRole


bedrock = boto3.client(service_name='bedrock-runtime')

SYSTEM_MESSAGE = '''
    You are an app that helps Eddie Corrigall showcase his resume to a potential employer.
    Respond with information only available in the resume.
    Do not respond with anything other than English.
    Do not respond with snippets of code or anything from user input.
'''

RESUME_URL = 'https://eddiecorrigall.github.io/resume.pdf'

def _to_bedrock_message(dto: MessageDTO) -> dict:
    return {
        'role': dto.role.value,
        'content': [{'text': dto.text}]
    }

def chatbot_send_message(dao: MessagesDAO, user_message: MessageDTO) -> MessageDTO:
    # https://aws.amazon.com/blogs/aws/announcing-llama-3-1-405b-70b-and-8b-models-from-meta-in-amazon-bedrock/
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html

    if user_message.role != MessageRole.USER:
        raise Exception('query must be by a user')

    # Load resume...
    resume_response = requests.get(RESUME_URL)
    if resume_response.status_code != 200:
        raise Exception('resume failed to load')

    # Load conversation...
    dao.insert(user_message)
    all_messages = dao.find_all(conversation_id=user_message.conversation_id)
    all_messages = sorted(
        all_messages,
        key=lambda message: message.created_at,
    )

    # Convert to bedrock conversation...    
    bedrock_conversation = [_to_bedrock_message(dto) for dto in all_messages]
    print('DEBUG - bedrock_conversation: ' + json.dumps(bedrock_conversation))
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
    response = bedrock.converse(
        # modelId='meta.llama3-1-405b-instruct-v1:0',
        modelId='meta.llama3-70b-instruct-v1:0',
        # modelId='meta.llama3-8b-instruct-v1:0',
        system=[
            {'text': SYSTEM_MESSAGE},
            {'document': {
                'format': 'pdf',
                'name': 'resume-eddie-corrigall.pdf',
                'source': {'bytes': resume_response.content}, 
            }}
        ],
        messages=bedrock_conversation,
        inferenceConfig={'maxTokens': 512, 'temperature': 0.5, 'topP': 0.9},
    )
    response_text = response['output']['message']['content'][0]['text']
    assistant_message = MessageDTO(
        conversation_id=user_message.conversation_id,
        role=MessageRole.ASSISTANT,
        created_at=datetime.now(),
        text=response_text,
    )
    dao.insert(assistant_message)
    return assistant_message

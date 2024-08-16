import boto3
import requests

from datetime import datetime
from typing import List

from dao import errors as dao_errors
from common import safe_serialize
from dto.document import DocumentDTO
from dao.messages import MessagesDAO
from dto.messages import MessageDTO, MessageRole
from services import errors as service_errors


bedrock = boto3.client(service_name='bedrock-runtime')

def _http_get(url: str) -> bytes:
    http_response = requests.get(url)
    if http_response.status_code != 200:
        raise Exception('http request for document failed')
    return http_response.content

def _to_bedrock_message(dto: MessageDTO) -> dict:
    content = [{'text': dto.text}]
    for document_dto in dto.documents:
        content.append({
            'document': {
                'name': document_dto.name,
                'format': document_dto.format.value,
                'source': {
                    'bytes': _http_get(document_dto.url),
                },
            },
        })
    return {
        'role': dto.role.value,
        'content': content,
    }

def chatbot_query(
    system_message_text: str,
    conversation: List[MessageDTO],
) -> str:
    # https://aws.amazon.com/blogs/aws/announcing-llama-3-1-405b-70b-and-8b-models-from-meta-in-amazon-bedrock/
    # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html

    # Convert to bedrock conversation...    
    bedrock_conversation = [_to_bedrock_message(dto) for dto in conversation]
    print('DEBUG - bedrock_conversation: ' + safe_serialize(bedrock_conversation))
    try:
        # https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
        response = bedrock.converse(
            # modelId='meta.llama3-1-405b-instruct-v1:0',
            modelId='meta.llama3-70b-instruct-v1:0',
            # modelId='meta.llama3-8b-instruct-v1:0',
            system=[
                {'text': system_message_text},
            ],
            messages=bedrock_conversation,
            inferenceConfig={
                # https://docs.aws.amazon.com/bedrock/latest/userguide/general-guidelines-for-bedrock-users.html
                'maxTokens': 512,
                'temperature': 0.5,  # the creativity of the response
                'topP': 0.9,  # stability of response
            },
        )
        response_text = response['output']['message']['content'][0]['text']
        return response_text
    except bedrock.exceptions.ThrottlingException as e:
        print(e)
        raise service_errors.TooManyRequestsError()

def chatbot_get_messages(
    dao: MessagesDAO,
    conversation_id: str,
) -> List[MessageDTO]:
    try:
        return dao.find_all(conversation_id=conversation_id)
    except dao_errors.NotFoundError:
        return []
    except dao_errors.TooManyRequestsError:
        raise service_errors.TooManyRequestsError()

def chatbot_send_message(
    dao: MessagesDAO,
    system_message_text: str,
    conversation_id: str,
    text: str,
    documents: List[DocumentDTO] = None,
    initial_document: DocumentDTO = None,
) -> MessageDTO:
    conversation = chatbot_get_messages(dao=dao, conversation_id=conversation_id)
    user_message = MessageDTO(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        created_at=datetime.now(),
        text=text,
        documents=(
            [initial_document] + (documents if documents else [])
            if not conversation and initial_document else
            # When there is no conversation history, include the initial document
            documents
        ),
    )
    conversation.append(user_message)
    conversation = sorted(
        conversation,
        key=lambda message: message.created_at,
    )
    chatbot_response = chatbot_query(
        system_message_text=system_message_text,
        conversation=conversation,
    )
    assistant_message = MessageDTO(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        created_at=datetime.now(),
        text=chatbot_response,
    )
    try:
        # TODO: batch insert messages
        dao.insert(user_message)
        dao.insert(assistant_message)
    except dao_errors.TooManyRequestsError:
        raise service_errors.TooManyRequestsError()
    return assistant_message

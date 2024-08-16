import boto3

from datetime import datetime, timedelta, timezone
from typing import List

from common import from_timestamp, to_timestamp
from dto.document import DocumentDTO, DocumentFormat, document_to_dict
from dao.errors import NotFoundError, TooManyRequestsError
from dto.messages import MessageDTO, MessageRole
from dao.common import BaseDAO


dynamodb = boto3.client(service_name='dynamodb')

def _to_dynamodb_message(dto: MessageDTO, expires_at: datetime = None) -> dict:
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ReservedWords.html
    item = {
        'ConversationID': dto.conversation_id,
        'CreatedAt': to_timestamp(dto.created_at),
        'MessageRole': dto.role.value,
        'MessageText': dto.text,
    }
    if dto.documents:
        item['MessageDocuments'] = [
            document_to_dict(document_dto)
            for document_dto in dto.documents
        ]
    if expires_at:
        item['ExpiresAt'] = to_timestamp(expires_at)
    return item

def _from_dynamodb_message(item: dict) -> MessageDTO:
    return MessageDTO(
        conversation_id=item['ConversationID']['S'],
        created_at=from_timestamp(int(item['CreatedAt']['N'])),
        role=MessageRole(item['MessageRole']['S']),
        text=item['MessageText']['S'],
        documents=(
            [
                DocumentDTO(
                    name=document_item['M']['name']['S'],
                    format=DocumentFormat(document_item['M']['format']['S']),
                    url=document_item['M']['url']['S'],
                )
                for document_item in item['MessageDocuments']['L']
            ]
            if 'MessageDocuments' in item else
            None
        ),
    )

class MessagesDAO(BaseDAO):
    def __init__(self):
        super().__init__(table_name='ChatbotMessages')

    def insert(self, dto: MessageDTO):
        expires_at = dto.created_at + timedelta(minutes=20)
        _table = self._get_table()
        try:
            # TODO: ConditionExpression to prevent replacement
            _table.put_item(
                Item=_to_dynamodb_message(dto, expires_at=expires_at),
            )
        except dynamodb.exceptions.ProvisionedThroughputExceededException | dynamodb.exceptions.RequestLimitExceeded as e:
            print(e)
            raise TooManyRequestsError()


    def find_all(self, conversation_id: str) -> List[MessageDTO]:
        try:
            response = dynamodb.query(
                TableName=self.table_name,
                ScanIndexForward=False,  # Descending sort by CreatedAt (sort/range key)
                Limit=100,  # Avoid too much history
                ConsistentRead=True,
                KeyConditionExpression='ConversationID = :id',
                ExpressionAttributeValues={
                    ':id': {'S': conversation_id},
                },
            )
        except dynamodb.exceptions.ResourceNotFoundException as e:
            print(e)
            raise NotFoundError()
        except dynamodb.exceptions.ProvisionedThroughputExceededException | dynamodb.exceptions.RequestLimitExceeded as e:
            print(e)
            raise TooManyRequestsError()
        items = response['Items']
        return [_from_dynamodb_message(item) for item in items]

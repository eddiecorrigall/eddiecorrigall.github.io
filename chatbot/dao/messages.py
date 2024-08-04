import boto3

from typing import List
from datetime import datetime, timedelta

from dto.messages import MessageDTO, MessageRole
from dao.common import BaseDAO


dynamodb = boto3.client(service_name='dynamodb')

def _to_dynamodb_message(dto: MessageDTO, expires_at: datetime = None) -> dict:
    item = {
        'ConversationID': dto.conversation_id,
        'CreatedAt': int(dto.created_at.timestamp()),
        'Type': dto.role.value,
        'Text': dto.text,
    }
    if expires_at:
        item['ExpiresAt'] = int(expires_at.timestamp())
    return item

def _from_dynamodb_message(item: dict) -> MessageDTO:
    return MessageDTO(
        conversation_id=item['ConversationID']['S'],
        created_at=datetime.fromtimestamp(int(item['CreatedAt']['N'])),
        role=MessageRole(item['Type']['S']),
        text=item['Text']['S'],
    )

class MessagesDAO(BaseDAO):
    def __init__(self):
        super().__init__(table_name='ChatbotMessages')

    def insert(self, dto: MessageDTO):
        expires_at = dto.created_at + timedelta(minutes=20)
        _table = self._get_table()
        _table.put_item(Item=_to_dynamodb_message(dto, expires_at=expires_at))

    def find_all(self, conversation_id: str) -> List[MessageDTO]:
        response = dynamodb.batch_get_item(
            RequestItems={
                self.table_name: {
                    'Keys': [
                        {
                            'ConversationID': {
                                'N': conversation_id,
                            },
                        },
                    ],
                    'ConsistentRead': True,
                    'ProjectionExpression': 'ConversationID, CreatedAt, Type, Text',
                }
            },
            ReturnConsumedCapacity='NONE'
        )
        items = response['Responses'][self.table_name]
        return [_from_dynamodb_message(item) for item in items]

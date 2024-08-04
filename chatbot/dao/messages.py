import boto3

from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from dto.messages import MessageDTO, MessageRole
from dao.common import BaseDAO


dynamodb = boto3.client(service_name='dynamodb')

def _to_dynamodb_message(dto: MessageDTO, expires_at: datetime = None) -> dict:
    item = {
        'ConversationID': dto.conversation_id,
        'CreatedAt': int(dto.created_at.timestamp()),
        'Role': dto.role.value,
        'Text': dto.text,
    }
    if expires_at:
        item['ExpiresAt'] = int(expires_at.timestamp())
    return item

def _from_dynamodb_message(item: dict) -> MessageDTO:
    return MessageDTO(
        conversation_id=item['ConversationID']['S'],
        created_at=datetime.fromtimestamp(int(item['CreatedAt']['N'])),
        role=MessageRole(item['Role']['S']),
        text=item['Text']['S'],
    )

def _create_messages_table(table_name: str) -> None:
    dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'ConversationID',
                'AttributeType': 'S',
            },
            {
                'AttributeName': 'CreatedAt',
                'AttributeType': 'N',
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'ConversationID',
                'KeyType': 'HASH',
            },
            {
                'AttributeName': 'CreatedAt',
                'KeyType': 'RANGE',
            },
        ],
        BillingMode='PAY_PER_REQUEST',
        SSESpecification={
            'Enabled': True,
        },
        TableClass='STANDARD',
        DeletionProtectionEnabled=True,
    )

class MessagesDAO(BaseDAO):
    def __init__(self):
        super().__init__(table_name='ChatbotMessages')

    def provision(self, **kwargs) -> Tuple[bool, Optional[str]]:
        return super().provision(_create_messages_table, **kwargs)

    def insert(self, dto: MessageDTO):
        expires_at = dto.created_at + timedelta(minutes=20)
        _table = self._get_table()
        _table.put_item(Item=_to_dynamodb_message(dto, expires_at=expires_at))

    def find_all(self, conversation_id: str) -> List[MessageDTO]:
        _table = self._get_table()
        response = _table.batch_get_item(
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
                    'ProjectionExpression': 'ConversationID, CreatedAt, Role, Text',
                }
            },
            ReturnConsumedCapacity='NONE'
        )
        items = response['Responses'][self.table_name]
        return [_from_dynamodb_message(item) for item in items]

import boto3

from typing import Any, Optional, Tuple
from collections.abc import Callable


dynamodb_resource = boto3.resource(service_name='dynamodb')
dynamodb = boto3.client(service_name='dynamodb')

class BaseDAO():
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def _get_table(self):
        return dynamodb_resource.Table(name=self.table_name)

    def exists(self) -> bool:
        try:
            self._get_table().table_status
            return True
        except dynamodb_resource.meta.client.exceptions.ResourceNotFoundException:
            return False

    def has_retention_policy(self) -> bool:
        try:
            response = dynamodb.describe_time_to_live(TableName=self.table_name)
            return response['TimeToLiveDescription']['TimeToLiveStatus'] == 'ENABLED'
        except:
            return False

    def enable_retention_policy(self):
        dynamodb.update_time_to_live(
            TableName=self.table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'ExpiresAt'
            }
        )

    def provision(self, create_table: Callable[[], Any], blocking: bool = False) -> Tuple[bool, Optional[str]]:
        if not self.exists():
            create_table()
            return False, 'waiting on table'
        if not self.has_retention_policy():
            self.enable_retention_policy()
            return False, 'waiting on retention policy'
        return True, None

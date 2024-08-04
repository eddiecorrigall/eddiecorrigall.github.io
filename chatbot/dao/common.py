import boto3


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

from cbaxter1988_utils.aws_dynamodb_utils import save_item, query_table_by_id, scan_table
from cbaxter1988_utils.daos.base_dao import BaseDAO


class DynamoDBDAO(BaseDAO):

    def __init__(self, table_id, **kwargs):
        self.table_id = table_id

    def save_item(self, item: dict):
        return save_item(table_id=self.table_id, item=item)

    def query_by_id(self, id: str):
        return query_table_by_id(table_id=self.table_id, id=id)

    def scan(self):
        return scan_table(table_id=self.table_id)

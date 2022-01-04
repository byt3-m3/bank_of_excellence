from cbaxter1988_utils.src.daos.dynamodb_dao import DynamoDBDAO
from cbaxter1988_utils.src.daos.mongodb_dao import MongoDBDAO

__all__ = [
    DynamoDBDAO,
    MongoDBDAO,
]

class Factory:

    def get_mongodb_dao(self):
        return MongoDBDAO(
            host="",
            port=0,
            db="",
            collection=""
        )
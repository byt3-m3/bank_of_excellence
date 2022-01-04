from typing import Union, List
from uuid import UUID

from bson import ObjectId
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pagination_utils import BasePaginator, BasePage
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult, UpdateResult, InsertOneResult, InsertManyResult

DEFAULT_ITEM_KEY = "_id"

logger = get_logger(__name__)


class InvalidUpdate(BaseException):
    """Exception for InvalidUpdate"""


class InvalidDelete(BaseException):
    """Exception for InvalidUpdate"""


def make_objectid() -> ObjectId:
    return ObjectId()


def get_client(db_host, db_port=27017) -> MongoClient:
    return MongoClient(host=db_host, port=db_port)


def get_mongo_client_w_auth(
        db_host: str,
        db_username: str,
        db_password: str,
        db_port: int = 27017,
        uuid_representation: str = 'standard'
) -> MongoClient:
    return MongoClient(
        host=db_host,
        port=db_port,
        username=db_username,
        password=db_password,
        uuidRepresentation=uuid_representation
    )


def get_database(client: MongoClient, db_name: str) -> Database:
    return client[db_name]


def get_collection(database: Database, collection: str) -> Collection:
    return database[collection]


def query_items(collection: Collection, query: dict) -> Cursor:
    return collection.find(query)


def scan_items(collection: Collection) -> Cursor:
    return collection.find()


def update_item(collection: Collection, item_id: Union[str, int], new_values: dict,
                item_key=DEFAULT_ITEM_KEY) -> UpdateResult:
    return collection.update_one(
        {
            f"{item_key}": item_id
        },
        {
            "$set": new_values
        }
    )


def add_item(collection: Collection, item: dict, key_id='_id') -> InsertOneResult:
    try:
        if not key_id == '_id':
            item['_id'] = item[key_id]

        return collection.insert_one(document=item)

    except DuplicateKeyError:
        raise


def delete_item(collection: Collection, item_id: Union[str, int], item_key=DEFAULT_ITEM_KEY) -> DeleteResult:
    return collection.delete_one(
        {
            f"{item_key}": item_id
        },

    )


def get_item(collection: Collection, item_id: Union[str, int, UUID], item_key=DEFAULT_ITEM_KEY) -> Cursor:
    return collection.find(
        {
            f"{item_key}": item_id
        }
    )


def get_page_from_collection(collection: Collection, query: dict, limit, last_item_id=None) -> BasePage:
    total_records = collection.find(query).count()

    if last_item_id:
        query.update({"_id": {"$gt": last_item_id}})

    cursor = collection.find(query).limit(limit)

    last_item_id = _get_last_id_from_cursor(cursor=cursor)

    return NewPage(
        cursor=cursor,
        last_id=last_item_id,
        total_items=total_records
    )


def get_pages_from_collection(collection: Collection, query: dict, page_size: int) -> BasePaginator:
    paginator = BasePaginator()
    items = collection.find(query)
    paginator.make_pages(items=items, page_size=page_size)
    return paginator


def _get_last_id_from_cursor(cursor):
    _cursor = clone_item(cursor)
    cursor_list = list(_cursor)
    try:
        return cursor_list[len(cursor_list) - 1].get("_id")

    except IndexError:
        return None


def _get_cursor_count(cursor):
    _cursor = clone_item(cursor)
    cursor_list = list(_cursor)
    return len(cursor_list)


def add_many_items(collection: Collection, items: List[dict], ordered: bool = True) -> InsertManyResult:
    return collection.insert_many(
        documents=items,
        ordered=ordered
    )


def check_for_items(collection: Collection):
    collection.aggregate()


def safe_update_item(collection: Collection, item_id: Union[UUID, str], expected_version: int, new_values: dict):
    """
    Preforms Optimistic Check by validating item version. If the expected_version does
    not match the document version, the transation will not be applied.

    Useful in distributed systems requiring safe updates to mongo records


    :param collection:
    :param item_id:
    :param expected_version:
    :param new_values:
    :return:
    """
    result = collection.update_one(
        filter={"version": expected_version, "_id": item_id},
        update={
            "$set": new_values,
            "$inc": {
                "version": 1
            }
        }
    )

    if result.raw_result.get("updatedExisting") is False:
        item = collection.find(filter={"_id": item_id}).next()
        raise InvalidUpdate(
            f"Version Number Mismatch, Expected:  '{expected_version}', Document Version: '{item.get('version')}'"
        )

    return result


def safe_delete_item(collection: Collection, item_id: Union[UUID, str], expected_version: int) -> DeleteResult:
    result = collection.delete_one(
        filter={"version": expected_version, "_id": item_id},

    )
    if result.raw_result.get("n") == 0:
        item = collection.find(filter={"_id": item_id}).next()
        raise InvalidDelete(
            f"Version Number Mismatch, Expected:  '{expected_version}', Document Version: '{item.get('version')}'"
        )

    return result


def add_database_user(database: Database, username, password, roles: List[str] = None):
    if roles is None:
        roles = []

    return database.command("createUser", username, pwd=password, roles=roles)


def add_database_user_rw(database: Database, username, password):
    return database.command("createUser", username, pwd=password, roles=['readWrite'])


def add_database_user_db_owner(database: Database, username, password):
    """
    The database owner can perform any administrative action on the database. This role combines the privileges granted by the readWrite, dbAdmin and userAdmin roles.


    :param database:
    :param username:
    :param password:
    :return:
    """
    return database.command("createUser", username, pwd=password, roles=['dbOwner'])


def add_admin_database_super_user(client: MongoClient, username, password):
    admin_db = get_database(db_name='admin', client=client)
    return admin_db.command(
        "createUser", username, pwd=password, roles=[
            "userAdminAnyDatabase", "readWriteAnyDatabase"])


def authenticate_database_basic(database: Database, username: str, password: str):
    return database.authenticate(username, password=password)


def remove_admin_database_user(client: MongoClient, username):
    admin_db = get_database(db_name='admin', client=client)
    return admin_db.command('dropUser', username)

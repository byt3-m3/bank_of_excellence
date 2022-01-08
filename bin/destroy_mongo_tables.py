from boe.env import (
    MONGO_HOST,
    MONGO_PORT,
    FAMILY_TABLE,
    TASK_TABLE,
    STORE_TABLE,
    APP_DB,
    BANK_ACCOUNT_TABLE
)
from boe.secrets import MONGO_DB_USERNAME, MONGO_DB_PASSWORD
from cbaxter1988_utils.pymongo_utils import get_mongo_client_w_auth, get_collection, get_database

client = get_mongo_client_w_auth(
    db_host=MONGO_HOST,
    db_username=MONGO_DB_USERNAME,
    db_password=MONGO_DB_PASSWORD,
    db_port=MONGO_PORT
)

tables = [
    FAMILY_TABLE,
    TASK_TABLE,
    STORE_TABLE,
    BANK_ACCOUNT_TABLE
]

for table in tables:
    collection = get_collection(
        database=get_database(client=client, db_name=APP_DB),
        collection=table
    )
    print(f'Dropping {table}')

    collection.drop()

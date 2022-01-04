from dataclasses import dataclass, asdict
from uuid import uuid5, UUID, NAMESPACE_DNS

from cbaxter1988_utils.pymongo_utils import (
    add_item,
    get_client,
    get_collection,
    get_database,
    get_item,
    safe_update_item,
    safe_delete_item,
    get_mongo_client_w_auth,
    add_admin_database_super_user,
    remove_admin_database_user
)
from pytest import fixture


@fixture()
def mongo_client_w_auth():
    return get_mongo_client_w_auth(
        db_host="192.168.1.5",
        db_port=27017,
        db_username='admin',
        db_password='pimpin12'
    )


@fixture()
def internal_database():
    client = get_mongo_client_w_auth(
        db_host="192.168.1.5",
        db_port=27017,
        db_username='admin',
        db_password='pimpin12'
    )
    db = get_database(client=client, db_name='LOCAL_BOE_MVP')

    return db


@dataclass
class PersonModel:
    _id: UUID
    first_name: str
    last_name: str
    version: int = 1


def _test_occ_update():
    person_model = PersonModel(
        _id=uuid5(NAMESPACE_DNS, f'Elijah'),
        first_name='Elijah',
        last_name='Baxter'
    )

    client = get_client(db_host='192.168.1.5', db_port=27017)
    database = get_database(client=client, db_name='test_db')
    collection = get_collection(database=database, collection='test_collection')
    item_id = UUID('be3a2142-c794-5817-9023-4764c36d0cdd')
    elijah_id = UUID('9607cc96-c17e-5af4-91cb-52aaeb182177')

    try:
        add_item(collection=collection, item=asdict(person_model))
    except Exception as err:
        print(err)

    item = get_item(collection=collection, item_id=item_id)
    data = item.next()

    expected_version = data.get("version")
    resp = safe_update_item(
        collection=collection,
        item_id=item_id,
        expected_version=expected_version,
        new_values={"last_name": "Baxter", "age": 6}
    )

    resp = safe_delete_item(collection=collection, item_id=elijah_id, expected_version=1)


# def _test_add_database_admin_user(internal_database):
#     add_database_admin_user(
#         database=internal_database,
#         username='admin',
#         password='admin'
#     )


def _test_add_item(internal_database):
    collection = get_collection(database=internal_database, collection="LOCAL_BANK_ACCOUNT_AGGREGATE_TABLE")
    result = add_item(collection=collection, item={"test": "test"})
    print(result.acknowledged)


def _test_add_admin_database_super_user(mongo_client_w_auth):
    add_admin_database_super_user(client=mongo_client_w_auth, username='cbaxter', password='password')


def _test_remove_admin_database_user(mongo_client_w_auth):
    remove_admin_database_user(client=mongo_client_w_auth, username='cbaxter')

import os
from uuid import UUID

from pytest import fixture


@fixture(autouse=True)
def set_stage():
    os.environ['STAGE'] = 'TEST'


@fixture
def set_env():
    INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
    SQLITE_DBNAME = "_db/test_event_db"

    os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
    os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME


@fixture
def set_persistence_test_env():
    INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
    SQLITE_DBNAME = "_db/persistence_events.sqllite"

    os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
    os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME


@fixture
def bank_account_uuid():
    return UUID("00000000-0000-0000-0000-000000000010")


@fixture
def bank_account_uuid_2():
    return UUID("00000000-0000-0000-0000-000000000011")


@fixture
def user_account_uuid():
    return UUID("00000000-0000-0000-0000-000000000001")


@fixture
def item_uuid():
    return UUID("00000000-0000-0000-0000-000000000100")


@fixture
def item_uuid_2():
    return UUID("00000000-0000-0000-0000-000000000101")


@fixture
def uuid4_2():
    return UUID("00000000-0000-0000-0000-000000000002")


@fixture
def uuid4_3():
    return UUID("00000000-0000-0000-0000-000000000003")


@fixture
def uuid4_4():
    return UUID("00000000-0000-0000-0000-000000000004")

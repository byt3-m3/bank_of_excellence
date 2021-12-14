from uuid import UUID

from pytest import fixture


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

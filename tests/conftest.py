from pytest import fixture
from uuid import UUID


@fixture
def uuid4_1():
    return UUID("00000000-0000-0000-0000-000000000001")


@fixture
def uuid4_2():
    return UUID("00000000-0000-0000-0000-000000000002")


@fixture
def uuid4_3():
    return UUID("00000000-0000-0000-0000-000000000003")


@fixture
def uuid4_4():
    return UUID("00000000-0000-0000-0000-000000000004")

from pytest import fixture
from uuid import UUID


@fixture
def uuid4_1():
    return UUID("184abb3f-be96-471c-8e18-f3b479939492")


@fixture
def uuid4_2():
    return UUID("03ae4da4-8544-4d19-8532-e67e092052ed")

@fixture
def uuid4_3():
    return UUID("ed45af8d-3c9c-434d-9aa2-1de4e1d39edc")

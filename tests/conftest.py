from pytest import fixture
from uuid import UUID


@fixture
def uuid4_mock():
    return UUID("184abb3f-be96-471c-8e18-f3b479939492")

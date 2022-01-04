from dataclasses import dataclass

import pytest
from tests.const import VAR_NAME


@pytest.fixture
def person_class():
    """
    Sample Person dataclass that can used in tests.

    :return:
    """

    @dataclass
    class Person:
        f_name: str

    return Person


@pytest.fixture
def person(person_class):
    """
    Sample Person instance that can be used in tests.

    :param person_class:
    :return:
    """
    return person_class(
        f_name=VAR_NAME
    )


@pytest.fixture()
def number_list():
    """
    List of 10 numbers

    :return:
    """
    return [
        i + 1 for i in range(10)
    ]

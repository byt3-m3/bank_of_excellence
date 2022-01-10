from boe.utils.core_utils import extract_name_from_object
import pytest
from dataclasses import dataclass


@dataclass
class CarModel:
    make: str


@pytest.fixture
def basic_model():
    return CarModel(
        make='Bmw'
    )


def test_extract_type(basic_model):
    expectation = extract_name_from_object(basic_model)

    assert expectation == 'CarModel'
    print(expectation)

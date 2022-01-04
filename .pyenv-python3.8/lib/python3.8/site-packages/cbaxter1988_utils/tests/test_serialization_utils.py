import base64
import datetime
import json
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from cbaxter1988_utils.serialization_utils import (
    serialize_object,
    rebuild_object,
    decode_b64_object,
    rebuild_decode_b64_object
)
from pytest import fixture


class CarTypeEnum(Enum):
    sedan = 1
    suv = 2


@dataclass
class Car:
    make: str
    model: str
    car_type: CarTypeEnum
    id: UUID


@dataclass
class Robot:
    data: bytes
    b64_data: bytes
    created: datetime.datetime = datetime.datetime.now()


def rebuild_car(make: str, model: str, car_type: int, id: str):
    return Car(
        make=make,
        model=model,
        car_type=CarTypeEnum(car_type),
        id=UUID(id)
    )


@fixture
def test_car_object():
    return Car(
        car_type=CarTypeEnum.sedan,
        make='bmw',
        model='5-series',
        id=UUID("c6a3d4c0-9805-4f03-aa20-4c511f7c75e1")
    )


@fixture
def test_robot_object():
    return Robot(
        data=b'TEST_DATA',
        b64_data=base64.b64encode(b'TEST_DATA'),
        created=datetime.datetime.fromisoformat("2021-12-22T23:23:56.763252")
    )


@fixture
def test_robot_dict():
    return {
        'data': 'TEST_DATA',
        'b64_data': 'VEVTVF9EQVRB',
        'created': '2021-12-22T23:23:56.763252'
    }


@fixture
def test_car_object_dict():
    return {
        "make": "bmw",
        "model": "5-series",
        "car_type": 1,
        "id": "c6a3d4c0-9805-4f03-aa20-4c511f7c75e1"
    }


@fixture
def b64_test_object():
    return b'eyJtYWtlIjogImJtdyIsICJtb2RlbCI6ICI1LXNlcmllcyIsICJjYXJfdHlwZSI6IDEsICJpZCI6ICJjNmEzZDRjMC05ODA1LTRmMDMtYWEyMC00YzUxMWY3Yzc1ZTEifQ=='


def test_serialize_object_when_decoding_base64(test_car_object, b64_test_object):
    data_bytes = serialize_object(test_car_object, b64_encode=True)
    assert data_bytes == b64_test_object
    assert isinstance(data_bytes, bytes)


def test_decode_b64_object(b64_test_object):
    data = decode_b64_object(b64_data=b64_test_object)
    assert isinstance(data, dict)
    assert data == {'make': 'bmw', 'model': '5-series', 'car_type': 1, 'id': 'c6a3d4c0-9805-4f03-aa20-4c511f7c75e1'}


def test_rebuild_object(test_car_object):
    json_string = serialize_object(test_car_object)

    data_dict = json.loads(json_string)

    car = rebuild_object(object_factory_func=rebuild_car, data=data_dict)
    assert isinstance(car, Car)


def test_rebuild_decode_b64_object(b64_test_object, test_car_object):
    car = rebuild_decode_b64_object(b64_data=b64_test_object, object_factory_func=rebuild_car)
    assert isinstance(car, Car)
    assert car == test_car_object


def test_serialize_object_when_processing_car_object(test_car_object, test_car_object_dict):
    json_string = serialize_object(test_car_object)
    assert json.loads(json_string) == test_car_object_dict


def test_serialize_object_when_processing_robot_object(test_robot_object, test_robot_dict):
    json_string = serialize_object(test_robot_object)
    print(json_string)
    json_data = json.loads(json_string)
    assert json_data == test_robot_dict

    #

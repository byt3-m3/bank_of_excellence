from boe.lib.common_models import Aggregate
from dataclasses import asdict, is_dataclass
from enum import Enum
from uuid import UUID


def _serialize_dict(item: dict):
    for key, val in item.items():
        if isinstance(val, Enum):
            item[key] = val.value


def _serialize_list(items: list):
    for i, item in enumerate(items):
        if isinstance(item, dict):
            _serialize_dict(item)

        if isinstance(item, list):
            _serialize_list(items=item)


def serialize_aggregate(model: Aggregate):
    data = asdict(model)

    for key, val in data.items():
        if isinstance(val, Enum):
            data[key] = val.value

        if isinstance(val, list):
            _serialize_list(items=val)

        if isinstance(val, dict):
            _serialize_dict(item=val)

    return data


def serialize_dataclass(model):
    data = asdict(model)

    for key, val in data.items():
        if isinstance(val, Enum):
            data[key] = val.value

    return data

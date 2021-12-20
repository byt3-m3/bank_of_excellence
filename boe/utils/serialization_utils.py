import datetime
from dataclasses import asdict
from enum import Enum
from typing import Union
from uuid import UUID

from boe.lib.common_models import Entity, AppEvent
from eventsourcing.domain import Aggregate


def _serialize_dict(item: dict, convert_id: bool=False):
    for key, val in item.items():
        if isinstance(val, UUID):
            item[key] = str(val)

        if isinstance(val, datetime.datetime):
            item[key] = str(val)

        if isinstance(val, Enum):
            item[key] = val.value


def _serialize_list(items: list):
    for i, item in enumerate(items):
        if isinstance(item, dict):
            _serialize_dict(item)

        if isinstance(item, list):
            _serialize_list(items=item)


def serialize_model(model: Union[Entity, Aggregate, AppEvent], convert_id: bool = False):
    data = asdict(model)
    if isinstance(model, Aggregate):
        data['version'] = model.version

    for key, val in data.items():
        if isinstance(val, Enum):
            data[key] = val.value

        if convert_id:
            if isinstance(val, UUID):
                data[key] = str(val)

        if isinstance(val, list):
            _serialize_list(items=val)

        if isinstance(val, dict):
            _serialize_dict(item=val, convert_id=convert_id)

    return data


def serialize_dataclass(model):
    data = asdict(model)

    for key, val in data.items():
        if isinstance(val, Enum):
            data[key] = val.value

    return data

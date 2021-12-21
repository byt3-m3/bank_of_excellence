from dataclasses import is_dataclass
from typing import Union

from boe.lib.common_models import Entity, AppEvent
from eventsourcing.domain import Aggregate
from serde.json import to_json, to_dict


def serialize_dataclass_to_json(model: Union[Entity, Aggregate, AppEvent], convert_id: bool = False):
    if is_dataclass(model):
        return to_json(model)
    else:
        raise ValueError(f'Invalid Type, Must be an instance of dataclasses.dataclass')


def serialize_dataclass_to_dict(model: Union[Entity, Aggregate, AppEvent], convert_id: bool = False):
    if is_dataclass(model):
        return to_dict(model)
    else:
        raise ValueError(f'Invalid Type, Must be an instance of dataclasses.dataclass')

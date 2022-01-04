import json
from base64 import b64encode, b64decode
from dataclasses import is_dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Union
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, UUID):
            return str(o)

        if isinstance(o, bytes):
            return o.decode()

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, dict):
            return self.default(o)

        return json.JSONEncoder.default(self, o)


def serialize_object(o: Any, b64_encode: bool = False) -> Union[str, bytes]:
    serialized_object = json.dumps(o, cls=CustomJSONEncoder)
    if b64_encode:
        return b64encode(serialized_object.encode())
    else:
        return serialized_object


def decode_b64_object(b64_data: bytes) -> dict:
    return json.loads(b64decode(b64_data).decode())


def rebuild_object(object_factory_func: callable, data: dict) -> Any:
    return object_factory_func(**data)


def rebuild_decode_b64_object(object_factory_func: callable, b64_data: bytes) -> Any:
    data = decode_b64_object(b64_data=b64_data)

    return rebuild_object(object_factory_func=object_factory_func, data=data)

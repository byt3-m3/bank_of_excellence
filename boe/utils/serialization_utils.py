import json

from cbaxter1988_utils.serialization_utils import serialize_object as _serialize_object


def serialize_object(o: object, b64_encode: bool = False):
    return _serialize_object(o=o, b64_encode=b64_encode)


def serialize_object_to_dict(o: object, b64_encode: bool = False):
    return json.loads(_serialize_object(o=o, b64_encode=b64_encode))

import base64
import json

from cbaxter1988_utils.aws_utils import get_event_bridge_client


def _get_client():
    return get_event_bridge_client()


def publish_event(
        source: str,
        event_bus_name: str,
        event_bus_arn: str,
        event_type: str,
        event_context: dict,
        encode: bool = False
):
    client = _get_client()
    return client.put_events(
        Entries=[
            {
                "Source": source,
                "EventBusName": event_bus_name,
                "Resources": [
                    event_bus_arn
                ],
                "DetailType": event_type,
                "Detail": event_context if not encode else base64.b64encode(f'{json.dumps(event_context)}'.encode()),
            }

        ]
    )


class EventManager:
    def __int__(self):
        pass

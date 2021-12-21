import json

from boe.env import AMQP_URL
from boe.lib.common_models import AppEvent, AppNotification
from boe.utils.core_utils import extract_type
from boe.utils.serialization_utils import serialize_dataclass_to_json
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher
from typing import Union

class PikaWorkerClient:
    def __init__(self, worker_que, worker_exchange, worker_routing_key):
        self.rabbit_client = make_basic_pika_publisher(
            amqp_url=AMQP_URL,
            queue=worker_que,
            exchange=worker_exchange,
            routing_key=worker_routing_key

        )

    def publish_event(self, event: Union[AppEvent, AppNotification]):
        self.rabbit_client.publish_message(
            body={
                extract_type(event): json.loads(serialize_dataclass_to_json(event))
            }
        )

    def publish(self, payload: dict):
        self.rabbit_client.publish_message(
            body=payload
        )

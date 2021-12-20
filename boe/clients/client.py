from boe.env import AMQP_URL
from boe.lib.common_models import AppEvent
from boe.utils.serialization_utils import serialize_model
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher


class PikaWorkerClient:
    def __init__(self, worker_que, worker_exchange, worker_routing_key):
        self.rabbit_client = make_basic_pika_publisher(
            amqp_url=AMQP_URL,
            queue=worker_que,
            exchange=worker_exchange,
            routing_key=worker_routing_key

        )

    def publish_event(self, event_name, event: AppEvent):
        self.rabbit_client.publish_message(
            body={
                event_name: serialize_model(event, convert_id=True)
            }
        )

    def publish(self, payload: dict):
        self.rabbit_client.publish_message(
            body=payload
        )

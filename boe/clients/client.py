from cbaxter1988_utils.pika_utils import make_basic_pika_publisher

from boe.env import AMPQ_URL, BANK_MANAGER_WORKER_QUEUE
from boe.utils.serialization_utils import serialize_aggregate


class PikaWorkerClient:
    def __init__(self):
        self.rabbit_client = make_basic_pika_publisher(
            amqp_url=AMPQ_URL,
            queue=BANK_MANAGER_WORKER_QUEUE,
            exchange="P_WORKER_EXCHANGE",
            routing_key="P_WORKER_KEY"

        )

    def _publish_event(self, event_name, event):
        self.rabbit_client.publish_message(
            body={
                event_name: serialize_aggregate(event, convert_id=True)
            }
        )

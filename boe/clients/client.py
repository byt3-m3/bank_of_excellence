import json
from typing import Union

import pika
from boe.env import AMQP_HOST, RABBITMQ_PASSWORD, RABBITMQ_USERNAME
from boe.lib.common_models import AppEvent, AppNotification
from boe.utils.core_utils import extract_type
from boe.utils.serialization_utils import serialize_object
from cbaxter1988_utils.pika_utils import make_pika_publisher


class PikaPublisherClient:
    def __init__(self, worker_exchange, worker_routing_key):
        self.publisher = make_pika_publisher(
            amqp_host=AMQP_HOST,
            amqp_username=RABBITMQ_USERNAME,
            amqp_password=RABBITMQ_PASSWORD,

        )

        self.exchange = worker_exchange
        self.routing_key = worker_routing_key

    def publish_event(self, event: Union[AppEvent, AppNotification], properties: pika.BasicProperties = None):
        self.publisher.publish_message(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=json.dumps({
                extract_type(event): json.loads(serialize_object(event))
            }),
            properties=properties
        )

    def publish(self, payload: dict, properties: pika.BasicProperties = None):
        self.publisher.publish_message(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=json.dumps(payload),
            properties=properties
        )

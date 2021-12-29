import json
import os

from boe.applications.store_domain_apps import (
    StoreManagerApp,
    NewStoreEvent,
    RemoveStoreItemEvent,
    NewStoreItemEvent,
    StoreManagerAppEventFactory
)
from boe.env import (
    AMQP_URL,
    STORE_MANAGER_WORKER_QUEUE,
    STORE_MANAGER_WORKER_EVENT_STORE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY,
    BOE_DLQ_EXCHANGE
)
from boe.lib.event_register import EventMapRegister
from boe.utils.app_event_utils import register_event_map
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_basic_pika_consumer, PikaQueueServiceWrapper
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosedByBroker
from pika.spec import Basic, BasicProperties

logger = get_logger("StoreManagerApp")

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = STORE_MANAGER_WORKER_EVENT_STORE

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

app = StoreManagerApp()

event_map_register = EventMapRegister()


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    event = json.loads(body)
    logger.info(f'Received msg: {body}')

    for event_name, payload in event.items():
        handler = event_map_register.get_event_handler(event_name=event_name)
        event_factory = event_map_register.get_event_factory(event_name=event_name)
        _event = event_factory(**payload)
        try:
            handler(_event)

            logger.info(f'Processed ApplicationEvent={_event}')

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            raise


def main():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMQP_URL
    )

    queue_service_wrapper.create_queue(
        queue=STORE_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    consumer = make_basic_pika_consumer(
        amqp_url=AMQP_URL,
        queue=STORE_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )

    try:
        event_map = {
            "NewStoreEvent": {
                "event_handler": app.handle_event,
                "event_factory": StoreManagerAppEventFactory.build_new_store_event,
                "event_class": NewStoreEvent
            },
            "NewStoreItemEvent": {
                "event_handler": app.handle_event,
                "event_factory": StoreManagerAppEventFactory.build_new_store_item_event,
                "event_class": NewStoreItemEvent
            },
            "RemoveStoreItemEvent": {
                "event_handler": app.handle_event,
                "event_factory": StoreManagerAppEventFactory.build_remove_store_item_event,
                "event_class": RemoveStoreItemEvent
            },

        }
        register_event_map(event_map_register=event_map_register, event_map=event_map)

        consumer.run()
    except ChannelClosedByBroker:
        consumer.run()


if __name__ == "__main__":
    main()

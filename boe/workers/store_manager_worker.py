import json

from boe.applications.store_domain_apps import (
    StoreManagerApp,
    NewStoreEvent,
    RemoveStoreItemEvent,
    NewStoreItemEvent,
    StoreManagerAppEventFactory
)
from boe.env import (
    AMQP_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_USERNAME,
    STORE_MANAGER_WORKER_QUEUE
)
from boe.lib.event_register import EventMapRegister
from boe.utils.app_event_utils import register_event_map
from boe.workers.env_setup import set_up_store_manager_worker_env, prepare_eventsourcing_postgres_env
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import PikaUtilsError, make_pika_queue_consumer_v2
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout
from pika.spec import Basic, BasicProperties

logger = get_logger("StoreManagerApp")

prepare_eventsourcing_postgres_env()

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
    set_up_store_manager_worker_env()

    consumer = make_pika_queue_consumer_v2(
        amqp_host=AMQP_HOST,
        amqp_password=RABBITMQ_PASSWORD,
        amqp_username=RABBITMQ_USERNAME,
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

        consumer.consume(prefetch_count=1)
    except (ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout, PikaUtilsError):
        consumer.consume(prefetch_count=1)


if __name__ == "__main__":
    main()

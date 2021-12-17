import json
import os

from boe.applications.store_domain_apps import (
    StoreManagerApp,
    StoreManagerAppEventFactory
)
from boe.env import AMPQ_URL, STORE_MANAGER_APP_QUEUE, SQLLITE_WORKER_EVENT_STORE
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_basic_pika_consumer
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = get_logger("StoreManagerApp")

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = SQLLITE_WORKER_EVENT_STORE

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

app = StoreManagerApp()

event_handler_map = {
    "NewStoreEvent": {
        "handler": app.handle_new_store_event,
        "event_factory": StoreManagerAppEventFactory.build_new_store_event
    }
}


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    event = json.loads(body)
    logger.info(f'Received msg: {body}')

    for event_name, payload in event.items():
        handler = event_handler_map.get(event_name)['handler']
        event_factory = event_handler_map.get(event_name)['event_factory']
        _event = event_factory(**payload)

        result = handler(event=_event)
        #
        logger.info(f'Processed ApplicationEvent={_event} - Handler={handler}')

        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    consumer = make_basic_pika_consumer(
        amqp_url=AMPQ_URL,
        queue=STORE_MANAGER_APP_QUEUE,
        on_message_callback=on_message_callback,
    )

    consumer.run()


if __name__ == "__main__":
    main()

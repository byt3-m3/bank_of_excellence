import json
import os

import pika.exceptions
from boe.applications.bank_domain_apps import BankDomainAppEventFactory
from boe.applications.bank_domain_apps import (
    BankManagerApp

)
from boe.env import AMPQ_URL, BANK_MANAGER_WORKER_QUEUE, BANK_MANAGER_WORKER_SQLITE_EVENT_STORE
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_basic_pika_consumer, PikaQueueServiceWrapper
from eventsourcing.application import AggregateNotFound
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = get_logger("bank_manager_worker")

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = BANK_MANAGER_WORKER_SQLITE_EVENT_STORE

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

bank_manager_app = BankManagerApp()

event_handler_map = {
    'EstablishNewAccountEvent': {
        "handler": bank_manager_app.handle_establish_new_account_event,
        "event_factory": BankDomainAppEventFactory.build_establish_new_account_event
    },
    'NewTransactionEvent': {
        "handler": bank_manager_app.handle_new_transaction_event,
        "event_factory": BankDomainAppEventFactory.build_new_transaction_event
    }
}


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    event = json.loads(body)
    logger.info(f'Received msg: {body}')
    for event_name, payload in event.items():
        handler = event_handler_map.get(event_name)['handler']
        event_factory = event_handler_map.get(event_name)['event_factory']
        _event = event_factory(**payload)
        try:
            result = handler(event=_event)

            logger.info(f'Processed ApplicationEvent={_event} - Handler={handler}')


        except AggregateNotFound as err:
            logger.warning(f"Handled AggregateNotFound Error: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            pass

        except Exception as error:
            logger.error(f'Unknown Error Encountered: {error}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            raise

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMPQ_URL
    )

    queue_service_wrapper.create_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue='BOE_ERRORS',
        dlq_exchange='BOE_ERROR_EXCHANGE',
        dlq_routing_key='BOE_ERROR_ROUTING_KEY'
    )

    consumer = make_basic_pika_consumer(
        amqp_url=AMPQ_URL,
        queue=BANK_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )
    try:

        consumer.run()
    except pika.exceptions.ChannelClosedByBroker:
        consumer.run()


if __name__ == "__main__":
    main()

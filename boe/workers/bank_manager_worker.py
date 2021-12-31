import json
import os

import pika.exceptions
from boe.applications.bank_domain_apps import BankDomainAppEventFactory
from boe.applications.bank_domain_apps import (
    BankManagerApp,
    EstablishNewAccountEvent,
    NewTransactionEvent

)
from boe.env import (
    AMQP_URL,
    BANK_MANAGER_WORKER_QUEUE,
    BANK_MANAGER_WORKER_EVENT_STORE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_EXCHANGE,
    BOE_DLQ_DEFAULT_ROUTING_KEY
)
from boe.lib.event_register import EventMapRegister
from boe.utils.app_event_utils import register_event_map
from boe.utils.metric_utils import MetricWriter
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_basic_pika_consumer, PikaQueueServiceWrapper, PikaUtilsError
from eventsourcing.application import AggregateNotFound
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = get_logger("bank_manager_worker")
metric_writer = MetricWriter()
INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = BANK_MANAGER_WORKER_EVENT_STORE

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

app = BankManagerApp()
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

            logger.info(f'Processed ApplicationEvent={_event} - Handler={handler}')


        except AggregateNotFound as err:
            logger.warning(f"Handled AggregateNotFound Error: {err}")

            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            metric_writer.publish_service_metric(
                metric_name='DLQException',
                service_name='BankManagerWorker',
                field_value=1,
                field_name='AggregateNotFound'
            )
            return


        except Exception as error:
            logger.error(f'Unknown Error Encountered: {error}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            metric_writer.publish_service_metric(
                metric_name='DLQException',
                service_name='BankManagerWorker',
                field_value=1,
                field_name=f'{error}'
            )
            return

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMQP_URL
    )

    queue_service_wrapper.create_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    consumer = make_basic_pika_consumer(
        amqp_url=AMQP_URL,
        queue=BANK_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )
    try:
        event_map = {
            'EstablishNewAccountEvent': {
                "event_factory": BankDomainAppEventFactory.build_establish_new_account_event,
                'event_class': EstablishNewAccountEvent,
                'event_handler': app.handle_event
            },
            'NewTransactionEvent': {
                "event_factory": BankDomainAppEventFactory.build_new_transaction_event,
                "event_class": NewTransactionEvent,
                'event_handler': app.handle_event
            }
        }
        register_event_map(event_map_register=event_map_register, event_map=event_map)
        consumer.run()
    except (pika.exceptions.ChannelClosedByBroker, pika.exceptions.StreamLostError, PikaUtilsError):
        consumer.run()


if __name__ == "__main__":
    main()

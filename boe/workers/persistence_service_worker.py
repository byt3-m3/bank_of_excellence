import json
import os
from dataclasses import dataclass

import pika.exceptions
from boe.applications.persistence_domain_app import PersistenceServiceApp, PersistenceDomainAppEventFactory
from boe.env import (
    AMQP_URL,
    PERSISTENCE_WORKER_QUEUE,
    PERSISTENCE_SERVICE_WORKER_EVENT_STORE,
    BOE_DLQ_EXCHANGE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY
)
from boe.lib.common_models import AppEvent
from boe.lib.domains.bank_domain import BankDomainWriteModel
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_basic_pika_consumer, PikaQueueServiceWrapper
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = get_logger("PersistenceServiceWorker")

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = PERSISTENCE_SERVICE_WORKER_EVENT_STORE

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

persistence_service_app = PersistenceServiceApp()


@dataclass(frozen=True)
class SaveBankAggregateEvent(AppEvent):
    data: str
    aggregate_type: str


bank_domain_write_model = BankDomainWriteModel()
write_model_map = {

    "PersistBankDomainAggregateEvent": {
        "handler": persistence_service_app.handle_persist_bank_domain_aggregate,
        "factory_func": PersistenceDomainAppEventFactory.build_persist_bank_domain_aggregate_event
    },
    "PersistFamilyUserAggregateEvent": {
        "handler": persistence_service_app.handle_persist_family_user_aggregate,
        "factory_func": PersistenceDomainAppEventFactory.build_persist_family_user_aggregate_event
    }
}


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    event = json.loads(body)
    logger.info(f'Received msg: {body}')

    for event_name, event_payload in event.items():
        try:
            payload = event_payload['payload']
            aggregate_id = event_payload['aggregate_id']
            payload_type = event_payload['payload_type']

            handler = write_model_map.get(event_name)['handler']
            factory_func = write_model_map.get(event_name)['factory_func']
            event_model = factory_func(
                aggregate_id=aggregate_id,
                payload=payload,
                payload_type=payload_type
            )

            handler(event=event_model)

        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            raise

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMQP_URL
    )

    queue_service_wrapper.create_queue(
        queue=PERSISTENCE_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    consumer = make_basic_pika_consumer(
        amqp_url=AMQP_URL,
        queue=PERSISTENCE_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )
    try:
        consumer.run()
    except pika.exceptions.ChannelClosedByBroker:
        consumer.run()


if __name__ == "__main__":
    main()

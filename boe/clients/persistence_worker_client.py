from boe.applications.persistence_domain_app import PersistenceDomainAppEventFactory
from boe.env import AMQP_URL, PERSISTENCE_WORKER_QUEUE
from boe.lib.domains.bank_domain import BankDomainAggregate
from boe.utils.serialization_utils import serialize_model
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher


class PersistenceWorkerClient:

    def __init__(self):
        self.app_event_factory = PersistenceDomainAppEventFactory()
        self.rabbit_client = make_basic_pika_publisher(
            amqp_url=AMQP_URL,
            queue=PERSISTENCE_WORKER_QUEUE,
            exchange="P_WORKER_EXCHANGE",
            routing_key="P_WORKER_KEY"

        )

    def publish_persist_bank_domain_aggregate_event(self, aggregate: BankDomainAggregate):
        event = self.app_event_factory.build_persist_bank_domain_aggregate_event(
            aggregate_id=str(aggregate.id),
            payload=serialize_model(aggregate),
            payload_type='PersistBankDomainAggregateEvent'
        )

        event_data = serialize_model(event, convert_id=True)
        self.rabbit_client.publish_message(
            body={
                "PersistBankDomainAggregateEvent": event_data
            }
        )

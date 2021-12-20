from boe.applications.persistence_domain_app import PersistenceDomainAppEventFactory
from boe.clients.client import PikaWorkerClient
from boe.env import PERSISTENCE_WORKER_QUEUE, STAGE
from boe.lib.domains.bank_domain import BankDomainAggregate
from boe.utils.serialization_utils import serialize_model


class PersistenceWorkerClient(PikaWorkerClient):

    def __init__(self):
        super().__init__(
            PERSISTENCE_WORKER_QUEUE,
            f"{STAGE}_PERSISTENCE_WORKER_EXCHANGE",
            f"{STAGE}_PERSISTENCE_WORKER_KEY"
        )
        self.app_event_factory = PersistenceDomainAppEventFactory()

    def publish_persist_bank_domain_aggregate_event(self, aggregate: BankDomainAggregate):
        event = self.app_event_factory.build_persist_bank_domain_aggregate_event(
            aggregate_id=str(aggregate.id),
            payload=serialize_model(aggregate),
            payload_type='PersistBankDomainAggregateEvent'
        )

        self.publish_event(
            event=event
        )

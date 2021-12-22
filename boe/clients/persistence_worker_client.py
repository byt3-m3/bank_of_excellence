import json

from boe.applications.persistence_domain_apps import PersistenceDomainAppEventFactory
from boe.clients.client import PikaWorkerClient
from boe.env import PERSISTENCE_WORKER_QUEUE, STAGE
from boe.lib.domains.bank_domain import BankDomainAggregate
from boe.lib.domains.user_domain import FamilyUserAggregate
from boe.utils.core_utils import extract_type
from boe.utils.serialization_utils import serialize_dataclass_to_json, serialize_dataclass_to_dict


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
            payload=json.loads(serialize_dataclass_to_json(aggregate)),
            payload_type='PersistBankDomainAggregateEvent'
        )

        self.publish_event(
            event=event
        )

    def publish_persist_family_aggregate_event(self, aggregate: FamilyUserAggregate):
        event = self.app_event_factory.build_persist_family_user_aggregate_event(
            aggregate_id=str(aggregate.id),
            payload=json.loads(serialize_dataclass_to_json(aggregate)),
            payload_type=extract_type(aggregate)
        )

        self.publish_event(
            event=event
        )

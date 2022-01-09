from boe.applications.persistence_domain_apps import PersistenceDomainAppEventFactory
from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, PERSISTENCE_QUEUE_ROUTING_KEY
from boe.lib.domains.bank_domain import BankDomainAggregate
from boe.lib.domains.user_domain import FamilyAggregate
from boe.utils.core_utils import extract_type
from boe.utils.serialization_utils import serialize_object_to_dict


class PersistenceWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(
            BOE_APP_EXCHANGE,
            PERSISTENCE_QUEUE_ROUTING_KEY
        )
        self.app_event_factory = PersistenceDomainAppEventFactory()

    def publish_persist_bank_domain_aggregate_event(self, aggregate: BankDomainAggregate):
        event = self.app_event_factory.build_persist_bank_domain_aggregate_event(
            aggregate_id=str(aggregate.id),
            payload=serialize_object_to_dict(aggregate),
            payload_type='PersistBankDomainAggregateEvent'
        )

        self.publish_event(
            event=event
        )

    def publish_persist_family_aggregate_event(self, aggregate: FamilyAggregate):
        event = self.app_event_factory.build_persist_family_user_aggregate_event(
            aggregate_id=str(aggregate.id),
            payload=serialize_object_to_dict(aggregate),
            payload_type=extract_type(aggregate)
        )

        self.publish_event(
            event=event
        )

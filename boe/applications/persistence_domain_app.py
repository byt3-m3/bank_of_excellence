from dataclasses import dataclass
from uuid import UUID

from boe.applications.transcodings import PersistenceRequestTranscoding, PersistenceRecordTranscoding
from boe.lib.common_models import AppEvent
from boe.lib.domains.bank_domain import BankDomainWriteModel
from boe.lib.domains.persistence_domain import PersistenceDomainFactory, PersistenceAggregate
from cbaxter1988_utils.log_utils import get_logger
from eventsourcing.application import Application, AggregateNotFound
from eventsourcing.persistence import Transcoder

logger = get_logger("PersistenceServiceApp")


@dataclass(frozen=True)
class PersistBankDomainAggregateEvent(AppEvent):
    aggregate_id: UUID
    payload: dict
    payload_type: str


class PersistenceDomainAppEventFactory:

    @staticmethod
    def build_persist_bank_domain_aggregate_event(aggregate_id: str, payload: dict, payload_type: str):
        return PersistBankDomainAggregateEvent(
            aggregate_id=UUID(aggregate_id),
            payload=payload,
            payload_type=payload_type
        )


class PersistenceServiceApp(Application):
    def __init__(self):
        super().__init__()
        self.persistence_domain_factory = PersistenceDomainFactory()
        self.bank_domain_write_model = BankDomainWriteModel()

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(PersistenceRequestTranscoding())
        transcoder.register(PersistenceRecordTranscoding())

    def get_persistence_aggregate(self, _id: UUID) -> PersistenceAggregate:
        return self.repository.get(aggregate_id=_id)

    def handle_persist_bank_domain_aggregate(self, event: PersistBankDomainAggregateEvent) -> UUID:
        try:
            aggregate = self.get_persistence_aggregate(_id=event.aggregate_id)

        except AggregateNotFound as err:
            logger.error(f'Encountered Error {AggregateNotFound}: "{str(err)}"')
            logger.warn(f"Aggregate: '{event.aggregate_id}' Not Found, Creating..")
            aggregate = self.persistence_domain_factory.build_persistence_aggregate(
                aggregate_id=event.aggregate_id,
                aggregate_type=event.payload_type
            )

        aggregate.persist_bank_aggregate(
            payload=event.payload
        )
        logger.info(f"Persisted {event.payload}")
        self.save(aggregate)
        return aggregate.id

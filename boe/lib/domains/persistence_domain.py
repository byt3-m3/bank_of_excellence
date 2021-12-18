import datetime
from dataclasses import dataclass
from typing import List
from uuid import uuid4, UUID

from boe.lib.common_models import Entity
from boe.lib.domains.bank_domain import BankDomainWriteModel, BankDomainFactory
from eventsourcing.domain import Aggregate, event


@dataclass
class PersistenceRequest(Entity):
    payload: dict
    payload_type: str
    created: datetime.datetime

    @property
    def created_time_stamp(self) -> int:
        return int(self.created.timestamp())


@dataclass
class PersistenceAggregate(Aggregate):
    requests: List[PersistenceRequest]

    def __init__(self, requests):
        self.bank_domain_write_model = BankDomainWriteModel()
        self.bank_domain_factory = BankDomainFactory()
        self.requests = requests

    @classmethod
    def create(cls, aggregate_id: UUID):
        return cls._create(
            cls.Created,
            id=aggregate_id,
            requests=[]
        )

    @event
    def new_persistence_request(self, payload: dict, payload_type: str, _id=None):
        request = PersistenceDomainFactory.build_persistence_request(
            payload=payload,
            payload_type=payload_type,
            _id=_id
        )

        self.requests.append(request)

    @event
    def persist_bank_aggregate(self, payload: dict):
        request = PersistenceDomainFactory.build_persistence_request(
            payload=payload,
            payload_type="BankAggregate",
            _id=payload.get("id")
        )

        self.bank_domain_write_model.save_bank_aggregate(
            aggregate=self.bank_domain_factory.rebuild_bank_domain_aggregate(
                **payload
            )
        )

        self.requests.append(request)


class PersistenceDomainFactory:
    @staticmethod
    def build_persistence_request(payload: dict, payload_type: str, _id=None):
        return PersistenceRequest(
            id=uuid4() if _id is None else _id,
            payload=payload,
            payload_type=payload_type,
            created=datetime.datetime.now()
        )

    @staticmethod
    def build_persistence_aggregate(aggregate_id: UUID):
        return PersistenceAggregate.create(
            aggregate_id=aggregate_id,
        )

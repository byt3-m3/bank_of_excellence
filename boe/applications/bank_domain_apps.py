from dataclasses import dataclass
from uuid import UUID

from boe.applications.transcodings import (
    BankAccountStateEnumTranscoding,
    BankTransactionMethodEnumTranscoding,
    BankTransactionEntityTranscoding,
    BankAccountEntityTranscoding
)
from boe.clients.notification_worker_client import NotificationWorkerClient
from boe.clients.persistence_worker_client import PersistenceWorkerClient
from boe.lib.common_models import AppEvent
from boe.lib.domains.bank_domain import (
    BankDomainFactory,
    BankTransactionMethodEnum,
    BankDomainWriteModel,
    BankDomainAggregate
)
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder


@dataclass(frozen=True)
class EstablishNewAccountEvent(AppEvent):
    owner_id: UUID
    is_overdraft_protected: bool


@dataclass(frozen=True)
class NewTransactionEvent(AppEvent):
    item_id: UUID
    account_id: UUID
    transaction_method: BankTransactionMethodEnum
    value: float


@dataclass(frozen=True)
class BankAccountCreatedNotification(AppEvent):
    account_id: str


@dataclass(frozen=True)
class BankTransactionProcessedNotification(AppEvent):
    account_id: str
    transaction_id: str


class BankDomainAppEventFactory:
    @staticmethod
    def build_establish_new_account_event(owner_id: str, is_overdraft_protected: bool):
        return EstablishNewAccountEvent(
            owner_id=UUID(owner_id),
            is_overdraft_protected=is_overdraft_protected
        )

    @staticmethod
    def build_new_transaction_event(
            item_id,
            account_id,
            transaction_method,
            value
    ):
        return NewTransactionEvent(
            item_id=UUID(item_id),
            account_id=UUID(account_id),
            transaction_method=BankTransactionMethodEnum(transaction_method),
            value=value
        )


class BankManagerApp(Application):
    def __init__(self):
        super().__init__()
        self.factory = BankDomainFactory()
        self.write_model = BankDomainWriteModel()
        self.persistence_worker_client = PersistenceWorkerClient()
        self.notification_worker_client = NotificationWorkerClient()

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(BankAccountEntityTranscoding())
        transcoder.register(BankAccountStateEnumTranscoding())
        transcoder.register(BankTransactionEntityTranscoding())
        transcoder.register(BankTransactionMethodEnumTranscoding())

    def handle_establish_new_account_event(self, event: EstablishNewAccountEvent) -> UUID:
        aggregate = self.factory.build_bank_domain_aggregate(
            owner_id=event.owner_id,
            is_overdraft_protected=event.is_overdraft_protected
        )

        self.save(aggregate)
        self.notification_worker_client.publish_app_event(
            event=BankAccountCreatedNotification(account_id=str(aggregate.id))
        )
        self.persistence_worker_client.publish_persist_bank_domain_aggregate_event(
            aggregate=aggregate
        )
        return aggregate.id

    def handle_new_transaction_event(self, event: NewTransactionEvent) -> UUID:
        transaction = self.factory.build_bank_transaction_entity(
            item_id=event.item_id,
            method=event.transaction_method,
            account_id=event.account_id,
            value=event.value
        )

        aggregate: BankDomainAggregate = self.repository.get(aggregate_id=event.account_id)
        aggregate.apply_transaction_to_account(transaction=transaction)

        self.save(aggregate)
        self.notification_worker_client.publish_app_event(
            event=BankTransactionProcessedNotification(
                account_id=str(aggregate.id),
                transaction_id=str(transaction.id)
            )
        )

        self.persistence_worker_client.publish_persist_bank_domain_aggregate_event(
            aggregate=aggregate
        )
        return aggregate.id

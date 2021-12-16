from dataclasses import dataclass
from uuid import uuid4, UUID

from boe.applications.transcodings import (
    BankAccountStateEnumTranscoding,
    BankTransactionMethodEnumTranscoding,
    BankTransactionEntityTranscoding,
    BankAccountEntityTranscoding
)
from boe.lib.common_models import AppEvent
from boe.lib.domains.bank_domain import (
    BankDomainFactory,
    BankTransactionMethodEnum,
    BankDomainWriteModel,
    BankDomainAggregate
)
from boe.utils.eventsourcing_utils import make_snapshot
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

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(BankAccountEntityTranscoding())
        transcoder.register(BankAccountStateEnumTranscoding())
        transcoder.register(BankTransactionEntityTranscoding())
        transcoder.register(BankTransactionMethodEnumTranscoding())

    def test_event(self):
        aggregate = self.factory.build_bank_domain_aggregate(
            owner_id=uuid4(),
            is_overdraft_protected=True
        )
        transaction = self.factory.build_bank_transaction_entity(
            item_id=uuid4(),
            method=BankTransactionMethodEnum.add,
            value=5,
            account_id=aggregate.id
        )

        aggregate.apply_transaction_to_account(transaction=transaction)
        snap_shot = make_snapshot(aggregate)

        print(snap_shot)
        self.save(aggregate)

    def handle_establish_new_account_event(self, event: EstablishNewAccountEvent) -> UUID:
        aggregate = self.factory.build_bank_domain_aggregate(
            owner_id=event.owner_id,
            is_overdraft_protected=event.is_overdraft_protected
        )

        self.write_model.save_bank_aggregate(aggregate=aggregate)

        self.save(aggregate)
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

        snapshot = make_snapshot(aggregate)
        self.write_model.save_bank_aggregate(aggregate=snapshot)
        self.save(aggregate)
        return aggregate.id

from uuid import uuid4

from boe.applications.transcodings import (
    BankAccountStateEnumTranscoding,
    BankTransactionMethodEnumTranscoding,
    BankTransactionEntityTranscoding,
    BankAccountEntityTranscoding
)
from boe.lib.domains.bank_domain import BankDomainFactory, BankTransactionMethodEnum
from boe.utils.eventsourcing_utils import make_snapshot
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder


class BankManagerApp(Application):
    def __init__(self):
        super().__init__()
        self.factory = BankDomainFactory()

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

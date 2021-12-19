from boe.applications.bank_domain_apps import BankDomainAppEventFactory
from boe.lib.domains.bank_domain import BankTransactionMethodEnum
from boe.clients.client import PikaWorkerClient


class BankManagerWorkerClient(PikaWorkerClient):

    def __init__(self):
        super().__init__()
        self.app_event_factory = BankDomainAppEventFactory()

    def publish_new_bank_account_event(self, owner_id: str):
        event = self.app_event_factory.build_establish_new_account_event(
            owner_id=owner_id,
            is_overdraft_protected=True
        )

        self._publish_event(event=event, event_name='EstablishNewAccountEvent')

    def publish_new_transaction_event(
            self,
            account_id: str,
            item_id: str,
            transaction_method: BankTransactionMethodEnum,
            value,
    ):
        event = self.app_event_factory.build_new_transaction_event(
            account_id=account_id,
            item_id=item_id,
            transaction_method=BankTransactionMethodEnum(transaction_method),
            value=value
        )

        self._publish_event(
            event_name='NewTransactionEvent',
            event=event
        )

from boe.applications.bank_domain_apps import BankDomainAppEventFactory
from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, BANK_MANAGER_QUEUE_ROUTING_KEY
from boe.lib.domains.bank_domain import BankTransactionMethodEnum


class BankManagerWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(
            worker_exchange=BOE_APP_EXCHANGE,
            worker_routing_key=BANK_MANAGER_QUEUE_ROUTING_KEY

        )
        self.app_event_factory = BankDomainAppEventFactory()

    def publish_new_bank_account_event(self, owner_id: str):
        event = self.app_event_factory.build_establish_new_account_event(
            owner_id=owner_id,
            is_overdraft_protected=True
        )

        self.publish_event(event=event)

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

        self.publish_event(

            event=event
        )

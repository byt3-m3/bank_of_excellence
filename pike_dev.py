from uuid import uuid4

from boe.clients.persistence_worker_client import PersistenceWorkerClient
from boe.clients.bank_manager_worker_client import BankManagerWorkerClient
from boe.env import AMPQ_URL, BANK_MANAGER_WORKER_QUEUE, STORE_MANAGER_APP_QUEUE, PERSISTENCE_WORKER_QUEUE
from boe.lib.domains.bank_domain import BankDomainFactory, BankTransactionMethodEnum
from boe.utils.serialization_utils import serialize_aggregate
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher

bank_manager_worker_client = BankManagerWorkerClient()


def publish_establish_new_account_event():
    account_id = str(uuid4())

    bank_manager_worker_client.publish_new_bank_account_event(
        owner_id=account_id
    )

    return account_id


def publish_new_transaction_event(account_id):
    bank_manager_worker_client.publish_new_transaction_event(
        item_id="00000000-0000-0000-0000-000000000010",
        account_id=account_id,
        transaction_method=BankTransactionMethodEnum.add,
        value=5
    )


def publish_new_store_event():
    publisher = make_basic_pika_publisher(
        amqp_url=AMPQ_URL,
        queue=STORE_MANAGER_APP_QUEUE,
        exchange="STORE_MANAGER_EXCHANGE",
        routing_key="STORE_MANAGER__KEY"
    )

    publisher.publish_message(
        body={
            "NewStoreEvent": {
                "family_id": str(uuid4())
            }
        }
    )


def publish_save_aggregate_event():
    publisher = make_basic_pika_publisher(
        amqp_url=AMPQ_URL,
        queue=PERSISTENCE_WORKER_QUEUE,
        exchange="P_WORKER_EXCHANGE",
        routing_key="P_WORKER_KEY"
    )

    client = PersistenceWorkerClient()

    bank_account_agg = BankDomainFactory.build_bank_domain_aggregate(owner_id=uuid4(), is_overdraft_protected=False)
    # print(bank_account_agg)
    data = serialize_aggregate(bank_account_agg)
    data['bank_account']['id'] = str(data['bank_account']['id'])
    data['bank_account']['owner_id'] = str(data['bank_account']['owner_id'])
    data['bank_account']['owner_id'] = str(data['bank_account']['owner_id'])

    client.publish_persist_bank_domain_aggregate_event(
        aggregate=bank_account_agg
    )


if __name__ == "__main__":
    # account_id = publish_establish_new_account_event()
    # publish_new_transaction_event(account_id=account_id)

    publish_save_aggregate_event()

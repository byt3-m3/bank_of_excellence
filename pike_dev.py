import datetime
from uuid import UUID
from uuid import uuid4

from boe.clients.bank_manager_worker_client import BankManagerWorkerClient
from boe.clients.persistence_worker_client import PersistenceWorkerClient
from boe.clients.user_manager_worker_client import UserManagerWorkerClient, SubscriptionTypeEnum
from boe.env import AMQP_URL, STORE_MANAGER_WORKER_QUEUE
from boe.lib.domains.bank_domain import BankDomainFactory, BankTransactionMethodEnum
from boe.utils.serialization_utils import serialize_dataclass_to_dict
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher


def publish_establish_new_account_event():
    bank_manager_worker_client = BankManagerWorkerClient()

    account_id = str(uuid4())

    bank_manager_worker_client.publish_new_bank_account_event(
        owner_id=account_id
    )

    return account_id


def publish_new_transaction_event(account_id):
    bank_manager_worker_client = BankManagerWorkerClient()

    bank_manager_worker_client.publish_new_transaction_event(
        item_id="00000000-0000-0000-0000-000000000010",
        account_id=account_id,
        transaction_method=BankTransactionMethodEnum.add,
        value=5
    )


def publish_new_store_event():
    publisher = make_basic_pika_publisher(
        amqp_url=AMQP_URL,
        queue=STORE_MANAGER_WORKER_QUEUE,
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
    client = PersistenceWorkerClient()

    bank_account_agg = BankDomainFactory.build_bank_domain_aggregate(owner_id=uuid4(), is_overdraft_protected=False)
    # print(bank_account_agg)
    data = serialize_dataclass_to_dict(bank_account_agg)
    print(data)
    # data['bank_account']['id'] = str(data['bank_account']['id'])
    # data['bank_account']['owner_id'] = str(data['bank_account']['owner_id'])
    # data['bank_account']['owner_id'] = str(data['bank_account']['owner_id'])
    #
    client.publish_persist_bank_domain_aggregate_event(
        aggregate=bank_account_agg
    )


def publish_new_family_event():
    client = UserManagerWorkerClient()

    client.publish_new_family_event(
        name="TEST",
        description="TEST",
        subscription_type=SubscriptionTypeEnum.premium
    )


def publish_new_child_account_event():
    client = UserManagerWorkerClient()

    client.publish_new_child_event(
        first_name='test',
        last_name='test',
        dob=datetime.datetime(year=2014, day=1, month=5),
        email='test@email.com',
        family_id=UUID("0371f817909d42a68161275dab445ad7"),
        grade=2
    )


def publish_family_subscription_change_event():
    client = UserManagerWorkerClient()

    client.publish_subscription_change_event(

        family_id=UUID("0371f817-909d-42a6-8161-275dab445ad7"),
        subscription_type=SubscriptionTypeEnum.premium
    )


def publish_create_cognito_user_event():
    client = UserManagerWorkerClient()

    client.publish_create_cognito_user_event(
        username="cbaxter",
        email="cbaxtertech@gmail.com",
        is_real=False

    )


if __name__ == "__main__":
    # account_id = publish_establish_new_account_event()
    # publish_new_transaction_event(account_id=account_id)

    publish_new_family_event()
    # publish_new_child_account_event()
    # publish_family_subscription_change_event()
    # publish_create_cognito_user_event()

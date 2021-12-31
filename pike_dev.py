import datetime
import time
from uuid import UUID
from uuid import uuid4

from boe.clients.bank_manager_worker_client import BankManagerWorkerClient
from boe.clients.user_manager_worker_client import UserManagerWorkerClient, SubscriptionTypeEnum
from boe.env import AMQP_URL, STORE_MANAGER_WORKER_QUEUE
from boe.lib.domains.bank_domain import BankTransactionMethodEnum
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


def publish_new_family_event():
    client = UserManagerWorkerClient()

    client.publish_new_family_event(
        name="TEST",
        description="TEST",
        subscription_type=SubscriptionTypeEnum.premium,
        first_name='Courtney',
        last_name='Baxter',
        dob=datetime.datetime(month=9, day=6, year=1988),
        email='cbaxtertech@gmail.com',
        id=str(uuid4())
    )


def publish_new_child_account_event():
    client = UserManagerWorkerClient()

    client.publish_new_child_event(
        first_name='test',
        last_name='test',
        dob=datetime.datetime(year=2014, day=1, month=5),
        email='test@email.com',
        family_id=UUID("3327375c-7857-4387-8076-a0e677bcc6a1"),
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
    # Bank Manager Events
    for i in range(100):
        account_id = publish_establish_new_account_event()

    # # for i in range(20):
        publish_new_transaction_event(account_id=account_id)
    #     time.sleep(.1)
    # User Manager Events
    # publish_new_family_event()
    publish_new_child_account_event()
    # publish_family_subscription_change_event()
    # publish_create_cognito_user_event()

    # Store Manager Events
    # publish_new_store_event()

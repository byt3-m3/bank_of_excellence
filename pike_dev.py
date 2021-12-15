from uuid import uuid4, UUID

from boe.env import AMPQ_URL, BANK_MANAGER_APP_QUEUE
from cbaxter1988_utils.pika_utils import make_basic_pika_publisher

publisher = make_basic_pika_publisher(
    amqp_url=AMPQ_URL,
    queue=BANK_MANAGER_APP_QUEUE,
    exchange="BANK_MANAGER_EXCHANGE",
    routing_key="BANK_MANAGER_KEY"
)


def publish_establish_new_account_event():
    publisher.publish_message(
        body={
            "EstablishNewAccountEvent": {
                "owner_id": str(uuid4()),
                "is_overdraft_protected": True
            }
        }
    )


def publish_new_transaction_event():
    account_id = UUID("19413fa4a1484663ad84eebba5f06a4f")

    publisher.publish_message(
        body={
            "NewTransactionEvent": {
                "item_id": "00000000-0000-0000-0000-000000000010",
                "account_id": "19413fa4a1484663ad84eebba5f06a4f",
                "transaction_method": 0,
                "value": 5
            }
        }
    )


if __name__ == "__main__":
    publish_new_transaction_event()

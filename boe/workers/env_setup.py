from boe.env import (
    AMQP_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_USERNAME,
    BANK_MANAGER_WORKER_QUEUE,
    USER_MANAGER_WORKER_QUEUE,
    STORE_MANAGER_WORKER_QUEUE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY,
    BOE_DLQ_EXCHANGE
)
from cbaxter1988_utils.pika_utils import make_pika_service_wrapper


def get_pika_service_wrapper():
    return make_pika_service_wrapper(
        amqp_host=AMQP_HOST,
        amqp_username=RABBITMQ_USERNAME,
        amqp_password=RABBITMQ_PASSWORD
    )


def set_up_bank_manager_worker_env():
    service_wrapper = get_pika_service_wrapper()

    service_wrapper.create_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )


def set_up_user_manager_worker_env():
    service_wrapper = get_pika_service_wrapper()

    service_wrapper.create_queue(
        queue=USER_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )


def set_up_store_manager_worker_env():
    service_wrapper = get_pika_service_wrapper()

    service_wrapper.create_queue(
        queue=STORE_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

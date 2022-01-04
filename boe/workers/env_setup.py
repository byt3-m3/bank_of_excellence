from boe.env import (
    AMQP_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_USERNAME,
    BANK_MANAGER_WORKER_QUEUE,
    USER_MANAGER_WORKER_QUEUE,
    STORE_MANAGER_WORKER_QUEUE,
    TASK_MANAGER_WORKER_QUEUE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY,
    BOE_APP_EXCHANGE,
    BANK_MANAGER_QUEUE_ROUTING_KEY,
    USER_MANAGER_QUEUE_ROUTING_KEY,
    STORE_MANAGER_QUEUE_ROUTING_KEY,
    TASK_MANAGER_QUEUE_ROUTING_KEY

)
from cbaxter1988_utils.pika_utils import make_pika_service_wrapper
from pika.spec import ExchangeType


def get_pika_service_wrapper():
    return make_pika_service_wrapper(
        amqp_host=AMQP_HOST,
        amqp_username=RABBITMQ_USERNAME,
        amqp_password=RABBITMQ_PASSWORD
    )


service_wrapper = get_pika_service_wrapper()


def _set_app_exchange():
    service_wrapper.create_exchange(
        exchange=BOE_APP_EXCHANGE,
        exchange_type=ExchangeType.direct,
        auto_delete=True

    )


def set_up_task_manager_worker_env():
    service_wrapper.create_queue(
        queue=TASK_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_APP_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    service_wrapper.bind_queue(
        queue=TASK_MANAGER_WORKER_QUEUE,
        exchange=BOE_APP_EXCHANGE,
        routing_key=TASK_MANAGER_QUEUE_ROUTING_KEY
    )


def set_up_bank_manager_worker_env():
    service_wrapper.create_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_APP_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    service_wrapper.bind_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        exchange=BOE_APP_EXCHANGE,
        routing_key=BANK_MANAGER_QUEUE_ROUTING_KEY
    )


def set_up_user_manager_worker_env():
    service_wrapper.create_queue(
        queue=USER_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_APP_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    service_wrapper.bind_queue(
        queue=USER_MANAGER_WORKER_QUEUE,
        exchange=BOE_APP_EXCHANGE,
        routing_key=USER_MANAGER_QUEUE_ROUTING_KEY
    )


def set_up_store_manager_worker_env():
    service_wrapper.create_queue(
        queue=STORE_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_APP_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    service_wrapper.bind_queue(
        queue=STORE_MANAGER_WORKER_QUEUE,
        exchange=BOE_APP_EXCHANGE,
        routing_key=STORE_MANAGER_QUEUE_ROUTING_KEY
    )


def set_up_exception_queues():
    service_wrapper.create_queue(
        queue=BOE_DLQ_QUEUE,
    )

    service_wrapper.bind_queue(
        queue=BOE_DLQ_QUEUE,
        exchange=BOE_APP_EXCHANGE,
        routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )


if __name__ == "__main__":
    _set_app_exchange()
    set_up_user_manager_worker_env()
    set_up_bank_manager_worker_env()
    set_up_store_manager_worker_env()
    set_up_task_manager_worker_env()

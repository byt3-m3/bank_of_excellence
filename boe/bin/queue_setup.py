from boe.env import (
    AMPQ_URL,
    BANK_MANAGER_WORKER_QUEUE,
    PERSISTENCE_WORKER_QUEUE,
    STORE_MANAGER_WORKER_QUEUE,
    NOTIFICATION_WORKER_QUEUE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY,
    BOE_DLQ_EXCHANGE
)
from cbaxter1988_utils.pika_utils import PikaQueueServiceWrapper


def validate_app_queues():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMPQ_URL
    )

    queue_service_wrapper.create_queue(
        queue=BANK_MANAGER_WORKER_QUEUE,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_support=True,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    queue_service_wrapper.create_queue(
        queue=PERSISTENCE_WORKER_QUEUE,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_support=True,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    queue_service_wrapper.create_queue(
        queue=STORE_MANAGER_WORKER_QUEUE,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_support=True,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    queue_service_wrapper.create_queue(
        queue=NOTIFICATION_WORKER_QUEUE,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_support=True,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )


if __name__ == "__main__":
    validate_app_queues()

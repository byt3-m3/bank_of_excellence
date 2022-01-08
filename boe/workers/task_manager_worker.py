import json

from boe.applications.task_domain_apps import (
    TaskManagerApp,
    TaskManagerAppEventFactory,

)
from boe.env import (
    AMQP_HOST,
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    TASK_MANAGER_WORKER_QUEUE

)
from boe.lib.event_register import EventMapRegister
from boe.workers.env_setup import set_up_task_manager_worker_env, prepare_eventsourcing_postgres_env
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_pika_queue_consumer_v2
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = get_logger("TaskManagerWorker")
event_map_register = EventMapRegister()

prepare_eventsourcing_postgres_env()

app = TaskManagerApp()

event_map_register.register_event(
    event_name='NewTaskEvent',
    event_class=TaskManagerAppEventFactory.NewTaskEvent,
    event_handler=app.handle_event,
    event_factory_func=TaskManagerAppEventFactory.build_new_task_event
)

event_map_register.register_event(
    event_name='MarkTaskCompleteEvent',
    event_class=TaskManagerAppEventFactory.MarkTaskCompleteEvent,
    event_handler=app.handle_event,
    event_factory_func=TaskManagerAppEventFactory.build_mark_task_complete_event
)

event_map_register.register_event(
    event_name='UpdateTaskValueEvent',
    event_class=TaskManagerAppEventFactory.UpdateTaskValueEvent,
    event_handler=app.handle_event,
    event_factory_func=TaskManagerAppEventFactory.build_update_task_value_event
)

event_map_register.register_event(
    event_name='AddEvidenceEvent',
    event_class=TaskManagerAppEventFactory.AddEvidenceEvent,
    event_handler=app.handle_event,
    event_factory_func=TaskManagerAppEventFactory.build_add_evidence_event
)


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    event_request = json.loads(body)
    logger.info(f'Received Request: {event_request}')

    for event_name, payload in event_request.items():
        _event_factory = event_map_register.get_event_factory(event_name=event_name)
        _event_handler = event_map_register.get_event_handler(event_name=event_name)
        _event_class = event_map_register.get_event_class(event_name=event_name)

        try:
            _event_model = _event_factory(**payload)
            _event_handler(_event_model)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Handled Event {_event_class}")
        except Exception as err:
            logger.error(f"Unhandled Exception: {err}")

            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            raise


def main():
    set_up_task_manager_worker_env()
    consumer = make_pika_queue_consumer_v2(
        amqp_host=AMQP_HOST,
        amqp_password=RABBITMQ_PASSWORD,
        amqp_username=RABBITMQ_USERNAME,
        queue=TASK_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )

    try:
        consumer.consume(prefetch_count=1)
    except Exception:
        raise


if __name__ == '__main__':
    main()

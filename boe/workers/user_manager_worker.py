import json
import os

from boe.applications.user_domain_apps import (
    UserManagerAppEventFactory,
    UserManagerApp,
    NewAdultAccountEvent,
    NewChildAccountEvent,
    FamilySubscriptionChangeEvent,
    CreateCognitoUserEvent,
    NewFamilyEvent
)
from boe.env import (
    AMQP_URL,
    USER_MANAGER_WORKER_QUEUE,
    BOE_DLQ_QUEUE,
    BOE_DLQ_DEFAULT_ROUTING_KEY,
    BOE_DLQ_EXCHANGE,
    USER_MANAGER_WORKER_EVENT_STORE

)
from boe.lib.event_handler import EventMapRegister
from cbaxter1988_utils.aws_cognito_utils import get_cognito_idp_client
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import PikaQueueServiceWrapper, make_basic_pika_consumer
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout
from pika.spec import Basic, BasicProperties

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = USER_MANAGER_WORKER_EVENT_STORE

os.environ['INFRASTRUCTUREADDASDWED_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

logger = get_logger('UserManagerWorker')

app = UserManagerApp()
app_event_factory = UserManagerAppEventFactory()

# AppEvents Registration
event_map_register = EventMapRegister()

event_map = {
    "NewFamilyEvent": {
        "event_factory": app_event_factory.build_new_family_event,
        "event_class": NewFamilyEvent
    },
    "NewChildAccountEvent": {
        "event_factory": app_event_factory.build_new_child_account_event,
        "event_class": NewChildAccountEvent
    },
    "FamilySubscriptionChangeEvent": {
        "event_factory": app_event_factory.build_family_subscription_change_event,
        "event_class": FamilySubscriptionChangeEvent
    },
    "CreateCognitoUserEvent": {
        "event_factory": app_event_factory.build_create_cognito_user_event,
        "event_class": CreateCognitoUserEvent
    },
    "NewAdultAccountEvent": {
        "event_factory": app_event_factory.build_new_adult_account_event,
        "event_class": NewAdultAccountEvent
    }
}

for event_name, event_options in event_map.items():
    event_map_register.register_event(
        event_name=event_name,
        event_handler=app.handle_event,
        event_factory_func=event_options['event_factory'],
        event_class=event_options['event_class'],
    )


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    cognito_client = get_cognito_idp_client()
    event = json.loads(body)
    logger.info(f'Received msg: {body}')

    for event_name, payload in event.items():
        event_factory = event_map_register.get_event_factory(event_name=event_name)
        event_class = event_map_register.get_event_class(event_name=event_name)
        handler = event_map_register.get_event_handler(event_name=event_name)

        _event = event_factory(**payload)
        if not isinstance(_event, event_class):
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            raise TypeError(f"Invalid Event type, must be of type {event_class}")

        try:
            handler(_event)
            logger.info(f'Processed ApplicationEvent={_event}')
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except (
                cognito_client.exceptions.UsernameExistsException,
                cognito_client.exceptions.LimitExceededException
        ) as err:
            logger.error(f'DLQ: Sending Event="{event}" -- Exception={err}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as error:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            logger.error(f'Unknown Error Encountered: {error}')
            raise


def main():
    queue_service_wrapper = PikaQueueServiceWrapper(
        amqp_url=AMQP_URL
    )

    queue_service_wrapper.create_queue(
        queue=USER_MANAGER_WORKER_QUEUE,
        dlq_support=True,
        dlq_queue=BOE_DLQ_QUEUE,
        dlq_exchange=BOE_DLQ_EXCHANGE,
        dlq_routing_key=BOE_DLQ_DEFAULT_ROUTING_KEY
    )

    consumer = make_basic_pika_consumer(
        amqp_url=AMQP_URL,
        queue=USER_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )

    try:

        consumer.run()
    except (ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout):
        consumer.run()


if __name__ == "__main__":
    main()

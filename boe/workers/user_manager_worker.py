import json

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
    AMQP_HOST,
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    USER_MANAGER_WORKER_QUEUE

)
from boe.lib.event_register import EventMapRegister
from boe.workers.env_setup import set_up_user_manager_worker_env, prepare_eventsourcing_postgres_env
from cbaxter1988_utils.aws_cognito_utils import get_cognito_idp_client
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.pika_utils import make_pika_queue_consumer_v2, PikaUtilsError
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout
from pika.spec import Basic, BasicProperties

logger = get_logger('UserManagerWorker')

prepare_eventsourcing_postgres_env()

app = UserManagerApp()
app_event_factory = UserManagerAppEventFactory()
event_map_register = EventMapRegister()


def register_event_map(event_map: dict):
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
    set_up_user_manager_worker_env()
    consumer = make_pika_queue_consumer_v2(
        amqp_host=AMQP_HOST,
        amqp_password=RABBITMQ_PASSWORD,
        amqp_username=RABBITMQ_USERNAME,
        queue=USER_MANAGER_WORKER_QUEUE,
        on_message_callback=on_message_callback,
    )

    try:

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

        register_event_map(event_map=event_map)
        consumer.consume(prefetch_count=1)
    except (ChannelClosedByBroker, StreamLostError, AMQPHeartbeatTimeout, PikaUtilsError):
        consumer.consume(prefetch_count=1)


if __name__ == "__main__":
    main()

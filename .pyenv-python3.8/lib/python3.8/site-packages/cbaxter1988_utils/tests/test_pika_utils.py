import os
from unittest.mock import patch

from cbaxter1988_utils.pika_utils import (
    make_basic_pika_publisher,
    PikaQueueConsumer,
    PikaServiceWrapper
)
from pytest import fixture

AMQP_USER = os.getenv("AMQP_USER", 'guest')
AMQP_PW = os.getenv("AMQP_PW", 'guest')
AMQP_HOST = os.getenv("AMQP_HOST", '192.168.1.5')
AMQP_PORT = os.getenv("AMQP_PORT", 5672)

AMQP_URL = os.getenv("AMPQ_URL", f"amqp://{AMQP_USER}:{AMQP_PW}@{AMQP_HOST}:{AMQP_PORT}")


@fixture
def test_queue_name():
    return 'PIKA_DEV_TEST_QUEUE'


@fixture
def test_queue_exchange_name():
    return 'PIKA_DEV_EXCHANGE'


@fixture
def test_queue_routing_key():
    return 'PIKA_DEV_ROUTING_KEY'


@fixture
def test_dlq_name():
    return 'PIKA_DEV_DLQ_TEST_QUEUE'


@fixture
def test_dlq_routing_key_name():
    return 'PIKA_DEV_DLQ_ROUTING_KEY'


@fixture
def test_dlq_exchange_name():
    return 'PIKA_DEV_DLQ_EXCHANGE'


@fixture
def blocking_connection_adapter_mock():
    with patch("cbaxter1988_utils.pika_utils.BlockingConnectionAdapter", autospec=True) as connector_mock:
        yield connector_mock


@fixture
def basic_pika_publisher_testable(test_queue_name, test_queue_exchange_name, test_queue_routing_key):
    return make_basic_pika_publisher(
        amqp_url=AMQP_URL,
        queue=test_queue_name,
        routing_key=test_queue_routing_key,
        exchange=test_queue_exchange_name
    )


@fixture
def pika_queue_service_wrapper_testable():
    return PikaServiceWrapper(
        amqp_url=AMQP_URL,

    )


def test_basic_publisher_when_publishing_message(blocking_connection_adapter_mock, basic_pika_publisher_testable):
    publisher = basic_pika_publisher_testable
    publisher.publish_message(body={
        "test": "test"
    })
    blocking_connection_adapter_mock.assert_called()


def test_pika_queue_service_wrapper_when_creating_queue(
        blocking_connection_adapter_mock,
        pika_queue_service_wrapper_testable,
        test_queue_name,
        test_dlq_name,
        test_dlq_routing_key_name,
        test_dlq_exchange_name
):
    queue_builder = pika_queue_service_wrapper_testable

    queue_builder.create_queue(
        queue=test_queue_name,
        dlq_support=True,
        dlq_queue=test_dlq_name,
        dlq_routing_key=test_dlq_routing_key_name,
        dlq_exchange=test_dlq_exchange_name
    )
    blocking_connection_adapter_mock.assert_called()


def test_pika_queue_service_wrapper_when_deleting_queue(
        blocking_connection_adapter_mock,
        pika_queue_service_wrapper_testable,
        test_queue_name
):
    queue_wrapper = pika_queue_service_wrapper_testable
    queue_wrapper.delete_queue(
        queue=test_queue_name,
        if_empty=False
    )

    blocking_connection_adapter_mock.assert_called()


def test_pika_queue_service_wrapper_when_purging_queue(
        blocking_connection_adapter_mock,
        pika_queue_service_wrapper_testable,
        test_queue_name
):
    queue_wrapper = pika_queue_service_wrapper_testable
    queue_wrapper.purge_queue(queue=test_queue_name)
    blocking_connection_adapter_mock.assert_called()


def test_pika_queue_consumer():
    def on_message_callback(ch, method, properties, body):
        print(ch, method, properties, body)

    consumer = PikaQueueConsumer(amqp_url=AMQP_URL, queue_name='TEST_QUEUE', callback=on_message_callback)

    consumer.consume()
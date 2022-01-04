import pika
from cbaxter1988_utils.log_utils import get_logger

logger = get_logger(__name__)

PREFETCH_COUNT = 1


class PikaUtilsError(BaseException):
    """Utils Exception"""


class RabbitConnection:
    """
    RabbitMQ Connection Context Manager

    """

    def __init__(self, host, user, password, port=5672, heartbeat=60):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.heartbeat = heartbeat

    def __enter__(self):
        logger.info('Entering Connection Context')
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=self.heartbeat
        )
        self.connection = pika.BlockingConnection(parameters)

        logger.info(f'Connected to {self.host} @ {self.port}')
        self.channel = self.connection.channel()
        logger.info(f'Opened Channel {self.channel.channel_number}')
        return self.channel

    def __exit__(self, exception_type, exception_value, traceback):
        logger.info('Exiting Connection Context')
        self.connection.close()
        logger.info(f'Closed Connection to host: {self.host}@{self.port}')


class PikaPublisher:
    def __init__(
            self,
            amqp_host: str,
            amqp_username: str,
            amqp_password: str,
            heartbeat: int = 60,
    ):
        self.amqp_host = amqp_host
        self.amqp_username = amqp_username
        self.amqp_password = amqp_password
        self.heartbeat = heartbeat

    def publish_message(self, exchange: str, routing_key: str, body: bytes, properties: pika.BasicProperties = None):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties
            )


class PikaQueueConsumerV2:
    def __init__(
            self,
            amqp_host: str,
            amqp_username: str,
            amqp_password: str,
            queue_name: str,
            callback: callable,
            heartbeat: int = 60,
    ):

        self._callback = callback
        self._queue_name = queue_name

        self.amqp_host = amqp_host
        self.amqp_username = amqp_username
        self.amqp_password = amqp_password
        self.heartbeat = heartbeat

    def consume(self, prefetch_count=None):

        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.basic_consume(queue=self._queue_name, on_message_callback=self._callback)
            if prefetch_count:
                channel.basic_qos(prefetch_count=prefetch_count)

            try:
                channel.start_consuming()
            except Exception:
                logger.error(f"Unknown Exception Caught, Closing active channel: {channel.channel_number}")
                channel.stop_consuming()
                raise


class PikaServiceWrapper:
    def __init__(self, amqp_host: str, amqp_username: str, amqp_password: str, heartbeat: int = 60):
        self.amqp_host = amqp_host
        self.amqp_username = amqp_username
        self.amqp_password = amqp_password
        self.heartbeat = heartbeat

    def create_queue(
            self,
            queue: str,
            dlq_queue: str = None,
            dlq_support: bool = False,
            dlq_exchange: str = None,
            dlq_routing_key: str = None
    ):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            queue_arguments = {}

            if dlq_support:
                channel.queue_declare(queue=dlq_queue)
                logger.info(f'Created Dead-Letter-Queue={dlq_queue}')
                channel.exchange_declare(exchange=dlq_exchange, auto_delete=True)
                logger.info(f'Created Dead-Letter-Queue exchange={dlq_exchange}')

                channel.queue_bind(queue=dlq_queue, exchange=dlq_exchange, routing_key=dlq_routing_key)
                logger.info(f'Bound Queue={dlq_queue} to exchange={dlq_exchange} and routing_key={dlq_routing_key}')
                queue_arguments['x-dead-letter-exchange'] = dlq_exchange
                queue_arguments['x-dead-letter-routing-key'] = dlq_routing_key

            channel.queue_declare(queue=queue, arguments=queue_arguments)

    def purge_queue(self, queue: str):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.queue_purge(queue=queue)

    def delete_queue(self, queue: str, if_empty: bool = False, if_unused: bool = False):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.queue_delete(queue=queue, if_empty=if_empty, if_unused=if_unused)

    def create_exchange(
            self,
            exchange,
            exchange_type: pika.spec.ExchangeType,
            passive: bool = False,
            auto_delete: bool = False
    ):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.exchange_declare(
                exchange=exchange,
                exchange_type=exchange_type.value,
                passive=passive,
                auto_delete=auto_delete
            )

    def bind_queue(self, queue: str, exchange: str, routing_key: str = None):
        with RabbitConnection(
                host=self.amqp_host,
                user=self.amqp_username,
                password=self.amqp_password,
                heartbeat=self.heartbeat
        ) as channel:
            channel.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=routing_key
            )


def make_amqp_url(amqp_user, amqp_pw, amqp_host, amqp_port):
    return f"amqp://{amqp_user}:{amqp_pw}@{amqp_host}:{amqp_port}"


def make_pika_queue_consumer_v2(
        amqp_host: str,
        amqp_username: str,
        amqp_password: str,
        queue: str,
        on_message_callback: callable,
) -> PikaQueueConsumerV2:
    """
     When Defining a callback function use the following signature:

    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

    def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        # Your Code Here

    """
    return PikaQueueConsumerV2(
        amqp_host=amqp_host,
        amqp_username=amqp_username,
        amqp_password=amqp_password,
        queue_name=queue,
        callback=on_message_callback
    )


def make_pika_publisher(
        amqp_host: str,
        amqp_username: str,
        amqp_password: str,
        heartbeat: int = 60
):
    return PikaPublisher(
        amqp_host=amqp_host,
        amqp_username=amqp_username,
        amqp_password=amqp_password,
        heartbeat=heartbeat
    )


def make_pika_service_wrapper(
        amqp_host: str,
        amqp_username: str,
        amqp_password: str,
        heartbeat: int = 60
):
    return PikaServiceWrapper(
        amqp_host=amqp_host,
        amqp_password=amqp_password,
        amqp_username=amqp_username,
        heartbeat=heartbeat
    )

from dataclasses import asdict

from boe.clients.client import PikaWorkerClient
from boe.env import NOTIFICATION_WORKER_QUEUE
from boe.lib.common_models import AppEvent
from boe.utils.core_utils import extract_type


class NotificationWorkerClient(PikaWorkerClient):

    def __init__(self):
        super().__init__(
            worker_que=NOTIFICATION_WORKER_QUEUE,
            worker_exchange="NOTIFICATION_WORKER_EXCHANGE",
            worker_routing_key='NOTIFICATION_WORKER_KEY'

        )

    def publish_app_event(self, event: AppEvent):
        self.publish(
            {
                extract_type(event): asdict(event)
            }
        )

from dataclasses import asdict

from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, NOTIFICATION_QUEUE_ROUTING_KEY
from boe.lib.common_models import AppEvent
from boe.utils.core_utils import extract_type


class NotificationWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(
            worker_exchange=BOE_APP_EXCHANGE,
            worker_routing_key=NOTIFICATION_QUEUE_ROUTING_KEY

        )

    def publish_app_event(self, event: AppEvent):
        self.publish(
            {
                extract_type(event): asdict(event)
            }
        )

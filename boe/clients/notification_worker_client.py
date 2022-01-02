from dataclasses import asdict

from boe.clients.client import PikaPublisherClient
from boe.env import STAGE
from boe.lib.common_models import AppEvent
from boe.utils.core_utils import extract_type


class NotificationWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(
            worker_exchange=f"{STAGE}_NOTIFICATION_WORKER_EXCHANGE",
            worker_routing_key=f'{STAGE}_NOTIFICATION_WORKER_KEY'

        )

    def publish_app_event(self, event: AppEvent):
        self.publish(
            {
                extract_type(event): asdict(event)
            }
        )

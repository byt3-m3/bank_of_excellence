from uuid import UUID

from boe.applications.store_domain_apps import StoreManagerAppEventFactory
from boe.clients.client import PikaPublisherClient
from boe.env import (
    BOE_APP_EXCHANGE,
    STORE_MANAGER_QUEUE_ROUTING_KEY
)


class StoreWorkerClient(PikaPublisherClient):
    def __init__(self):
        super().__init__(

            BOE_APP_EXCHANGE,
            STORE_MANAGER_QUEUE_ROUTING_KEY,

        )
        self.event_factory = StoreManagerAppEventFactory()

    def publish_new_store_event(self, family_id: UUID):
        event = self.event_factory.build_new_store_event(
            family_id=str(family_id)
        )
        self.publish_event(event=event)

    def publish_new_store_item_event(
            self,
            family_id: UUID,
            item_name: str,
            item_description: str,
            item_value: float
    ):
        event = self.event_factory.build_new_store_item_event(
            store_id=str(family_id),
            item_name=item_name,
            item_value=item_value,
            item_description=item_description,

        )

        self.publish_event(
            event=event
        )

    def publish_remove_store_item_event(self, store_id: UUID, item_id: UUID):
        event = self.event_factory.build_remove_store_item_event(
            item_id=str(item_id),
            store_id=str(store_id)
        )

        self.publish_event(
            event=event
        )

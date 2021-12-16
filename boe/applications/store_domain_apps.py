from dataclasses import dataclass
from uuid import UUID

from boe.applications.transcodings import StoreEntityTranscoding
from boe.lib.common_models import AppEvent
from boe.lib.domains.store_domain import (
    StoreDomainWriteModel,
    StoreAggregate,
    StoreDomainFactory
)
from cbaxter1988_utils.log_utils import get_logger
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = get_logger("StoreManagerApp")


@dataclass(frozen=True)
class NewStoreEvent(AppEvent):
    family_id: UUID


@dataclass(frozen=True)
class NewStoreItemEvent(AppEvent):
    store_id: UUID
    item_name: str
    item_description: str
    item_value: float


class StoreManagerAppEventFactory:

    @staticmethod
    def build_new_store_event(family_id: str):
        return NewStoreEvent(
            family_id=UUID(family_id)
        )

    @staticmethod
    def build_new_store_item_event(
            store_id: str,
            item_name: str,
            item_description: str,
            item_value: float
    ):
        return NewStoreItemEvent(
            store_id=UUID(store_id),
            item_name=item_name,
            item_value=item_value,
            item_description=item_description
        )

class StoreManagerApp(Application):

    def __init__(self):
        super().__init__()
        self.write_model = StoreDomainWriteModel()
        self.factory = StoreDomainFactory()

    def get_store(self, aggregate_id: UUID) -> StoreAggregate:
        return self.repository.get(aggregate_id=aggregate_id)

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(StoreEntityTranscoding())

    def handle_new_store_event(self, event: NewStoreEvent) -> UUID:
        store_aggregate = self.factory.build_store_aggregate(
            family_id=event.family_id
        )

        self.write_model.save_store_aggregate(aggregate=store_aggregate)
        self.save(store_aggregate)
        logger.info(f"Created Store: {store_aggregate.id}")
        return store_aggregate.id

    def handle_new_store_item_event(self, event: NewStoreItemEvent) -> UUID:
        store = self.get_store(aggregate_id=event.store_id)

        store.new_store_item(
            description=event.item_description,
            name=event.item_name,
            value=event.item_value
        )

        self.write_model.save_store_aggregate(aggregate=store)
        self.save(store)

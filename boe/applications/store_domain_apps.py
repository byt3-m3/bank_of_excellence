from dataclasses import dataclass
from functools import singledispatchmethod
from logging import getLogger
from uuid import UUID

from boe.applications.transcodings import StoreEntityTranscoding, StoreItemEntityTranscoding
from boe.lib.common_models import AppEvent
from boe.lib.domains.store_domain import (
    StoreDomainWriteModel,
    StoreAggregate,
    StoreDomainFactory
)
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = getLogger("StoreManagerApp")


@dataclass(frozen=True)
class NewStoreEvent(AppEvent):
    family_id: UUID


@dataclass(frozen=True)
class NewStoreItemEvent(AppEvent):
    store_id: UUID
    item_name: str
    item_description: str
    item_value: float


@dataclass(frozen=True)
class RemoveStoreItemEvent(AppEvent):
    store_id: UUID
    item_id: UUID


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

    @staticmethod
    def build_remove_store_item_event(
            store_id: str,
            item_id: str
    ):
        return RemoveStoreItemEvent(
            store_id=UUID(store_id),
            item_id=UUID(item_id)
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
        transcoder.register(StoreItemEntityTranscoding())

    def _save_aggregate(self, aggregate: StoreAggregate):
        self.save(aggregate)
        self.write_model.save_store_aggregate(
            aggregate=aggregate
        )

    @singledispatchmethod
    def handle_event(self, event):
        raise NotImplementedError(f"Invalid Event Type, {event}")

    @handle_event.register(NewStoreEvent)
    def _(self, event: NewStoreEvent) -> UUID:
        store_aggregate = self.factory.build_store_aggregate(
            family_id=event.family_id
        )

        self._save_aggregate(aggregate=store_aggregate)

        logger.info(f"Created Store: {store_aggregate.id}")
        return store_aggregate.id

    @handle_event.register(NewStoreItemEvent)
    def _(self, event: NewStoreItemEvent) -> UUID:
        store = self.get_store(aggregate_id=event.store_id)

        store_item = self.factory.build_store_item_entity(
            description=event.item_description,
            name=event.item_name,
            value=event.item_value
        )

        store.new_store_item(store_item=store_item)

        self._save_aggregate(aggregate=store)
        logger.info(f"Added Item='{store_item.id}' to Store='{store.id}'")
        return store.id

    @handle_event.register(RemoveStoreItemEvent)
    def _(self, event: RemoveStoreItemEvent) -> UUID:
        store = self.get_store(aggregate_id=event.store_id)
        store.remove_store_item(
            item_id=str(event.item_id)
        )

        self._save_aggregate(aggregate=store)
        logger.info(f"Removed Item='{event.item_id}' from Store='{store.id}'")
        return store.id

    # def handle_new_store_event(self, event: NewStoreEvent) -> UUID:
    #     store_aggregate = self.factory.build_store_aggregate(
    #         family_id=event.family_id
    #     )
    #
    #     self._save_aggregate(aggregate=store_aggregate)
    #
    #     logger.info(f"Created Store: {store_aggregate.id}")
    #     return store_aggregate.id

    # def handle_new_store_item_event(self, event: NewStoreItemEvent) -> UUID:
    #     store = self.get_store(aggregate_id=event.store_id)
    #
    #     store_item = self.factory.build_store_item_entity(
    #         description=event.item_description,
    #         name=event.item_name,
    #         value=event.item_value
    #     )
    #
    #     store.new_store_item(store_item=store_item)
    #
    #     self._save_aggregate(aggregate=store)
    #     logger.info(f"Added Item='{store_item.id}' to Store='{store.id}'")
    #     return store.id

    # def handle_remove_store_item_event(self, event: RemoveStoreItemEvent) -> UUID:
    #     store = self.get_store(aggregate_id=event.store_id)
    #     store.remove_store_item(
    #         item_id=str(event.item_id)
    #     )
    #
    #     self._save_aggregate(aggregate=store)
    #     logger.info(f"Removed Item='{event.item_id}' from Store='{store.id}'")
    #     return store.id

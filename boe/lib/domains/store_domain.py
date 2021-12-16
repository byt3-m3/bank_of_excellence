from boe.lib.common_models import Entity
from uuid import UUID, uuid4
from typing import Dict
from eventsourcing.domain import Aggregate, event
from dataclasses import dataclass, asdict


@dataclass
class StoreItemEntity(Entity):
    value: float
    name: str
    description: str


@dataclass
class StoreEntity(Entity):
    family_id: UUID


@dataclass
class StoreAggregate(Aggregate):
    store: StoreEntity
    store_item_map: Dict[UUID, dict]

    def _update_store_item_map(self, item: StoreItemEntity):
        if item.id not in self.store_item_map.keys():
            self.store_item_map[item.id] = asdict(item)
        else:
            self.store_item_map.update({item.id: asdict(item)})

    @property
    def store_item_ids(self):
        return [item_id for item_id in self.store_item_map.keys()]

    @property
    def store_items(self):
        return [item for item in self.store_item_map.values()]

    @event
    def new_store_item(self, name: str, value: float, description: str):
        store_item = StoreDomainFactory.build_store_item_entity(
            name=name,
            value=value,
            description=description
        )
        self._update_store_item_map(item=store_item)

    @event
    def remove_store_item(self, item_id: UUID):
        self.store_item_map.pop(item_id)


class StoreDomainFactory:
    @staticmethod
    def build_store_item_entity(
            value: float,
            description: str,
            name: str
    ) -> StoreItemEntity:
        return StoreItemEntity(
            id=uuid4(),
            value=value,
            description=description,
            name=name,
        )

    @staticmethod
    def build_store_entity(family_id: UUID, ) -> StoreEntity:
        return StoreEntity(
            id=uuid4(),
            family_id=family_id
        )

    @staticmethod
    def build_store_aggregate(family_id: UUID) -> StoreAggregate:
        return StoreAggregate(
            store=StoreDomainFactory.build_store_entity(
                family_id=family_id
            ),
            store_item_map={}
        )

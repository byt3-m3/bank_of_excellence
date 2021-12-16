from dataclasses import dataclass, asdict
from typing import Dict, List
from uuid import UUID, uuid4

from boe.env import MONGO_HOST, MONGO_PORT, APP_DB, STORE_TABLE
from boe.lib.common_models import Entity
from boe.utils.serialization_utils import serialize_aggregate
from cbaxter1988_utils.pymongo_utils import (
    add_item,
    update_item,
    get_client,
    get_database,
    get_collection
)
from eventsourcing.domain import Aggregate, event
from pymongo.errors import DuplicateKeyError


@dataclass(frozen=True)
class StoreTableModel:
    store_id: UUID
    store_items: List[dict]


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

    @classmethod
    def create(cls, store: StoreEntity, store_item_map: Dict[UUID, dict]):
        return cls._create(
            cls.Created,
            id=store.family_id,
            store=store,
            store_item_map=store_item_map
        )

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


class StoreDomainWriteModel:

    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_store_aggregate(self, aggregate: StoreAggregate):
        collection = get_collection(database=self.db, collection=STORE_TABLE)

        model = StoreTableModel(
            store_id=aggregate.id,
            store_items=aggregate.store_items
        )
        serialized_data = serialize_aggregate(model=model)
        try:
            add_item(collection=collection, item=serialized_data, key_id='store_id')
        except DuplicateKeyError:
            update_item(collection=collection, item_id=aggregate.id, new_values=serialized_data)


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
        return StoreAggregate.create(
            store=StoreDomainFactory.build_store_entity(
                family_id=family_id
            ),
            store_item_map={}
        )
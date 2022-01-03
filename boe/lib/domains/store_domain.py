from dataclasses import dataclass
from typing import Dict, List
from uuid import UUID, uuid4

from boe.env import MONGO_HOST, MONGO_PORT, APP_DB, STORE_TABLE
from boe.lib.common_models import Entity
from boe.secrets import MONGO_DB_USERNAME, MONGO_DB_PASSWORD
from boe.utils.serialization_utils import serialize_object_to_dict
from bson.binary import Binary, UuidRepresentation
from cbaxter1988_utils.pymongo_utils import (
    add_item,
    update_item,
    get_mongo_client_w_auth,
    get_database,
    get_collection,
    get_item
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
    store_item_map: Dict[str, StoreItemEntity]

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
            self.store_item_map[str(item.id)] = item

        else:
            self.store_item_map.update({str(item.id): item})

    @property
    def store_item_ids(self):
        return [item_id for item_id in self.store_item_map.keys()]

    @property
    def store_items(self):
        return [item for item in self.store_item_map.values()]

    @event
    def new_store_item(self, store_item: StoreItemEntity):
        self._update_store_item_map(item=store_item)

    @event
    def remove_store_item(self, item_id: str):
        self.store_item_map.pop(item_id)


class StoreDomainWriteModel:

    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_username=MONGO_DB_USERNAME,
            db_password=MONGO_DB_PASSWORD
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_store_aggregate(self, aggregate: StoreAggregate):
        collection = get_collection(database=self.db, collection=STORE_TABLE)

        serialized_data = serialize_object_to_dict(o=aggregate)
        _record_id = Binary.from_uuid(aggregate.id, uuid_representation=UuidRepresentation.STANDARD)

        serialized_data['_id'] = _record_id

        try:
            add_item(collection=collection, item=serialized_data)
        except DuplicateKeyError:
            update_item(collection=collection, item_id=_record_id, new_values=serialized_data)


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


class StoreDomainQueryModel:
    @dataclass(frozen=True)
    class StoreItemModel:
        item_id: UUID
        name: str
        value: str
        description: str

    @dataclass(frozen=True)
    class StoreModel:
        store_id: UUID
        store_items: List

    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_username=MONGO_DB_USERNAME,
            db_password=MONGO_DB_PASSWORD
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def _build_store_models(self, records):
        models = []
        for record in records:
            model = self.StoreModel(
                store_id=record['_id'],
                store_items=[
                    self.StoreItemModel(
                        item_id=UUID(item['id']),
                        description=item['description'],
                        name=item['name'],
                        value=item['value'],
                    )

                    for item in record['store_item_map'].values()
                ]
            )

            models.append(model)

        return models

    def get_store_by_id(self, store_id: UUID) -> StoreModel:
        collection = get_collection(self.db, collection=STORE_TABLE)

        records = list(get_item(collection, item_id=store_id))
        print(records)
        if len(records) == 0:
            return

        if len(records) == 1:
            models = self._build_store_models(records=records)

            print(models)

            return models[0]

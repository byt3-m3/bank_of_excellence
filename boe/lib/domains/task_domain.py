from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import singledispatchmethod
from uuid import UUID, uuid4

from boe.env import (
    MONGO_HOST,
    MONGO_PORT,

    APP_DB,
    TASK_TABLE
)
from boe.lib.common_models import Entity
from boe.secrets import MONGO_DB_PASSWORD, MONGO_DB_USERNAME
from boe.utils.serialization_utils import serialize_object_to_dict
from cbaxter1988_utils.pymongo_utils import (
    get_mongo_client_w_auth,
    get_database,
    add_item,
    query_items,
    update_item,
    get_collection
)
from eventsourcing.domain import Aggregate, event
from pymongo.errors import DuplicateKeyError


class TaskStatusEnum(Enum):
    complete = 0
    incomplete = 1
    awarded = 2


@dataclass
class TaskEntity(Entity):
    owner_id: UUID
    name: str
    description: str
    status: TaskStatusEnum
    value: float
    evidence_required: bool
    due_date: datetime
    is_validated: bool = False
    evidence_data: bytes = None
    created: datetime = datetime.now()


@dataclass
class TaskAggregate(Aggregate):
    task: TaskEntity

    @classmethod
    def create(cls, task: TaskEntity):
        return cls._create(
            cls.Created,
            id=task.id,
            task=task
        )

    @event
    def make_task_complete(self, status=TaskStatusEnum.complete):
        self.task.status = status

    @event
    def add_task_evidence(self, data: bytes):
        self.task.evidence_data = data

    @event
    def change_value(self, value: float):
        self.task.value = value


class TaskDomainFactory:

    @staticmethod
    def build_task_entity(
            owner_id: str,
            name: str,
            description: str,
            due_date: datetime,
            evidence_required: bool,
            value: float,
            _id=None

    ) -> TaskEntity:
        return TaskEntity(
            id=uuid4() if _id is None else _id,
            owner_id=UUID(owner_id),
            name=name,
            description=description,
            status=TaskStatusEnum.incomplete,
            due_date=due_date,
            evidence_required=evidence_required,
            value=value
        )

    @staticmethod
    def build_task_aggregate(
            owner_id: str,
            name: str,
            description: str,
            due_date: datetime,
            evidence_required: bool,
            value: float
    ) -> TaskAggregate:
        return TaskAggregate.create(
            task=TaskDomainFactory.build_task_entity(
                owner_id=owner_id,
                name=name,
                description=description,
                due_date=due_date,
                evidence_required=evidence_required,
                value=value
            )
        )


class TaskDomainWriteModel:
    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_password=MONGO_DB_PASSWORD,
            db_username=MONGO_DB_USERNAME
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    @singledispatchmethod
    def save_aggregate(self, aggregate):
        raise TypeError(f"Invalid Type {type(aggregate)}")

    @save_aggregate.register(TaskAggregate)
    def _(self, aggregate: TaskAggregate):
        serialized_aggregate = serialize_object_to_dict(aggregate)

        collection = get_collection(database=self.db, collection=TASK_TABLE)

        serialized_aggregate['_id'] = aggregate.id
        serialized_aggregate['version'] = aggregate.version

        try:
            add_item(item=serialized_aggregate, collection=collection, key_id='_id')
        except DuplicateKeyError:
            update_item(new_values=serialized_aggregate, item_id=aggregate.id, collection=collection)


class TaskDomainQueryModel:
    @dataclass(frozen=True)
    class TaskModel:
        task_id: UUID
        owner_id: UUID
        due_date: datetime
        created: datetime
        value: float
        is_validated: bool
        status: TaskStatusEnum
        name: str
        description: str

    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_password=MONGO_DB_PASSWORD,
            db_username=MONGO_DB_USERNAME
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def get_tasks_by_owner_id(self, owner_id: UUID):
        collection = get_collection(database=self.db, collection=TASK_TABLE)
        results = list(query_items(collection=collection, query={"task.owner_id": str(owner_id)}))

        return [
            self.TaskModel(
                owner_id=task_data['task']["owner_id"],
                created=datetime.fromisoformat(task_data['task']["created"]) if isinstance(task_data['task']["created"],
                                                                                           str) else task_data['task'][
                    "created"],
                due_date=datetime.fromisoformat(task_data['task']["due_date"]) if isinstance(
                    task_data['task']["due_date"],
                    str) else task_data['task']["due_date"],
                is_validated=task_data['task']["is_validated"],
                status=TaskStatusEnum(task_data['task']["status"]),
                task_id=task_data['_id'],
                value=task_data['task']["value"],
                name=task_data['task']["name"],
                description=task_data['task']["description"],
            )

            for task_data in results
        ]

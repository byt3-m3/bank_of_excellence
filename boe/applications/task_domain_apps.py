from dataclasses import dataclass
from datetime import datetime
from functools import singledispatchmethod
from uuid import UUID

import cbaxter1988_utils.log_utils
from boe.applications.transcodings import (
    TaskEntityTranscoding,
    TaskStatusEnumTranscoding,
    BytesTranscoding
)
from boe.lib.common_models import AppEvent
from boe.lib.domains.task_domain import (
    TaskAggregate,
    TaskDomainFactory,
    TaskDomainWriteModel,
    TaskStatusEnum
)
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = cbaxter1988_utils.log_utils.get_logger("TaskDomainApps")


class TaskManagerAppEventFactory:
    @dataclass(frozen=True)
    class NewTaskEvent(AppEvent):
        owner_id: UUID
        name: str
        description: str
        status: TaskStatusEnum
        value: float
        evidence_required: bool
        due_date: datetime

    @dataclass(frozen=True)
    class UpdateTaskValueEvent(AppEvent):
        task_id: UUID
        value: float

    @dataclass(frozen=True)
    class AddEvidenceEvent(AppEvent):
        task_id: UUID
        data: bytes

    @dataclass(frozen=True)
    class MarkTaskCompleteEvent(AppEvent):
        task_id: UUID

    @classmethod
    def build_new_task_event(
            cls,
            owner_id: str,
            name: str,
            description: str,
            due_date: datetime,
            evidence_required: bool,
            value: float,
            **kwargs

    ) -> NewTaskEvent:
        return cls.NewTaskEvent(
            owner_id=UUID(owner_id),
            name=name,
            description=description,
            status=TaskStatusEnum.incomplete,
            due_date=due_date,
            evidence_required=evidence_required,
            value=value
        )

    @classmethod
    def build_mark_task_complete_event(
            cls,
            task_id: str
    ) -> "TaskManagerAppEventFactory.MarkTaskCompleteEvent":
        return cls.MarkTaskCompleteEvent(
            task_id=UUID(task_id)
        )

    @classmethod
    def build_update_task_value_event(
            cls,
            task_id: str,
            value: float
    ) -> "TaskManagerAppEventFactory.UpdateTaskValueEvent":
        return cls.UpdateTaskValueEvent(
            task_id=UUID(task_id),
            value=value
        )

    @classmethod
    def build_add_evidence_event(
            cls,
            task_id: str,
            data: bytes
    ) -> "TaskManagerAppEventFactory.AddEvidenceEvent":
        return cls.AddEvidenceEvent(
            task_id=UUID(task_id),
            data=data
        )


class TaskManagerApp(Application):
    def __init__(self):
        super().__init__()
        self.factory = TaskDomainFactory()
        self.write_model = TaskDomainWriteModel()

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(TaskEntityTranscoding())
        transcoder.register(TaskStatusEnumTranscoding())
        transcoder.register(TaskStatusEnumTranscoding())
        transcoder.register(BytesTranscoding())

    def get_task_aggregate(self, task_id: UUID) -> TaskAggregate:
        return self.repository.get(task_id)

    def _save_aggregate(self, aggregate: TaskAggregate):
        self.write_model.save_aggregate(aggregate)
        self.save(aggregate)

    @singledispatchmethod
    def handle_event(self, event):
        raise NotImplementedError(f'Invalid Event {event}')

    @handle_event.register(TaskManagerAppEventFactory.NewTaskEvent)
    def _(self, event: TaskManagerAppEventFactory.NewTaskEvent):
        task_aggregate = self.factory.build_task_aggregate(
            value=event.value,
            due_date=event.due_date,
            description=event.description,
            owner_id=str(event.owner_id),
            evidence_required=event.evidence_required,
            name=event.name
        )
        self.write_model.save_aggregate(task_aggregate)

        self.save(task_aggregate)
        return task_aggregate.id

    @handle_event.register(TaskManagerAppEventFactory.MarkTaskCompleteEvent)
    def _(self, event: TaskManagerAppEventFactory.MarkTaskCompleteEvent):
        task_aggregate = self.get_task_aggregate(task_id=event.task_id)
        task_aggregate.make_task_complete()

        self.write_model.save_aggregate(task_aggregate)
        self.save(task_aggregate)

    @handle_event.register(TaskManagerAppEventFactory.UpdateTaskValueEvent)
    def _(self, event: TaskManagerAppEventFactory.UpdateTaskValueEvent):
        aggregate = self.get_task_aggregate(task_id=event.task_id)

        aggregate.change_value(value=event.value)

        self._save_aggregate(aggregate)

        return aggregate.id

    @handle_event.register(TaskManagerAppEventFactory.AddEvidenceEvent)
    def _(self, event: TaskManagerAppEventFactory.AddEvidenceEvent):
        aggregate = self.get_task_aggregate(task_id=event.task_id)

        if aggregate.task.evidence_required:
            aggregate.add_task_evidence(data=event.data)

        self._save_aggregate(aggregate=aggregate)

        return aggregate.id

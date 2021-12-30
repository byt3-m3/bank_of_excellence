from dataclasses import dataclass
from datetime import datetime
from functools import singledispatchmethod
from uuid import UUID

from boe.applications.transcodings import TaskEntityTranscoding, TaskStatusEnumTranscoding
from boe.lib.common_models import AppEvent
from boe.lib.domains.task_domain import (
    TaskAggregate,
    TaskDomainFactory,
    TaskDomainWriteModel,
    TaskStatusEnum
)
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder


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
class MarkTaskCompleteEvent(AppEvent):
    task_id: UUID


class TaskDomainAppEventFactory:
    @staticmethod
    def build_new_task_event(
            owner_id: str,
            name: str,
            description: str,
            due_date: datetime,
            evidence_required: bool,
            value: float

    ) -> NewTaskEvent:
        return NewTaskEvent(
            owner_id=UUID(owner_id),
            name=name,
            description=description,
            status=TaskStatusEnum.incomplete,
            due_date=due_date,
            evidence_required=evidence_required,
            value=value
        )

    @staticmethod
    def build_mark_task_complete_event(task_id: str) -> MarkTaskCompleteEvent:
        return MarkTaskCompleteEvent(
            task_id=UUID(task_id)
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

    def get_task_aggregate(self, task_id: UUID) -> TaskAggregate:
        return self.repository.get(task_id)

    @singledispatchmethod
    def handle_event(self, event):
        raise NotImplementedError(f'Invalid Event {event}')

    @handle_event.register(NewTaskEvent)
    def _(self, event: NewTaskEvent):
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

    @handle_event.register(MarkTaskCompleteEvent)
    def _(self, event: MarkTaskCompleteEvent):
        task_aggregate = self.get_task_aggregate(task_id=event.task_id)
        task_aggregate.make_task_complete()

        self.write_model.save_aggregate(task_aggregate)
        self.save(task_aggregate)

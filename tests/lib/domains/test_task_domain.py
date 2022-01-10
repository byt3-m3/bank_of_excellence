import datetime
import uuid

from boe.lib.domains.task_domain import (
    TaskDomainFactory,
    TaskStatusEnum,
    TaskAggregate
)
from pytest import fixture


@fixture
def task_aggregate_evidence_required_testable():
    return TaskDomainFactory.build_task_aggregate(
        owner_id='583e7cd9-9c70-4573-8d27-996aaa27a43c',
        due_date=datetime.datetime(year=2024, day=1, month=1),
        evidence_required=False,
        value=50,
        name='Clean Room',
        description='Clean you room',
        _id=str(uuid.uuid4())
    )


@fixture
def task_aggregate_evidence_not_required_testable():
    return TaskDomainFactory.build_task_aggregate(
        owner_id='583e7cd9-9c70-4573-8d27-996aaa27a43c',
        due_date=datetime.datetime(year=2024, day=1, month=1),
        evidence_required=False,
        value=50,
        name='Clean Room',
        description='Clean you room'
    )


def test_task_aggregate_when_created(task_aggregate_evidence_required_testable):
    task_aggregate = task_aggregate_evidence_required_testable
    assert isinstance(task_aggregate, TaskAggregate)


def test_task_aggregate_when_marking_complete(task_aggregate_evidence_required_testable):
    task_aggregate = task_aggregate_evidence_required_testable

    task_aggregate.mark_task_complete()

    assert task_aggregate.task.status is TaskStatusEnum.complete


def test_task_aggregate_when_changing_value(task_aggregate_evidence_required_testable):
    task_aggregate = task_aggregate_evidence_required_testable

    task_aggregate.change_value(value=300)

    assert task_aggregate.task.value == 300

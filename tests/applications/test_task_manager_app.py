import datetime
import uuid
from unittest.mock import patch

from boe.applications.task_domain_apps import (
    TaskManagerApp,
    TaskManagerAppEventFactory,
    TaskStatusEnum
)
from pytest import fixture


@fixture
def write_model_mock():
    with patch("boe.applications.task_domain_apps.TaskDomainWriteModel") as client_mock:
        yield client_mock


@fixture
def task_manager_app_testable():
    return TaskManagerApp()


@fixture
def new_task_event():
    return TaskManagerAppEventFactory.build_new_task_event(
        owner_id='a38c5bdc-f079-40f6-a9c5-8be227e17dfd',
        evidence_required=False,
        due_date=datetime.datetime(year=2022, day=2, month=12),
        description='Test Task',
        name='TestTask',
        value=5.00
    )


@fixture
def new_task_event_evidence_required():
    return TaskManagerAppEventFactory.build_new_task_event(
        owner_id='a38c5bdc-f079-40f6-a9c5-8be227e17dfd',
        evidence_required=True,
        due_date=datetime.datetime(year=2022, day=2, month=12),
        description='Test Task',
        name='TestTask',
        value=5.00
    )


def test_task_manager_app_when_handling_new_task_event(write_model_mock, task_manager_app_testable, new_task_event):
    app = task_manager_app_testable

    task_id = app.handle_event(new_task_event)
    assert isinstance(task_id, uuid.UUID)
    aggregate = app.get_task_aggregate(task_id=task_id)
    assert aggregate.id == task_id
    assert aggregate.task.owner_id == new_task_event.owner_id
    write_model_mock.assert_called()


def test_task_manager_app_when_handling_mark_task_complete_event(
        write_model_mock,
        task_manager_app_testable,
        new_task_event):
    app = task_manager_app_testable

    task_id = app.handle_event(new_task_event)

    mark_task_complete_event = TaskManagerAppEventFactory.build_mark_task_complete_event(task_id=str(task_id))

    app.handle_event(mark_task_complete_event)

    task = app.get_task_aggregate(task_id=task_id)

    assert task.task.status is TaskStatusEnum.complete
    write_model_mock.assert_called()


def test_task_manager_app_when_handling_update_task_value_event(
        write_model_mock,
        task_manager_app_testable,
        new_task_event_evidence_required
):
    app = task_manager_app_testable
    task_id = app.handle_event(new_task_event_evidence_required)

    event = TaskManagerAppEventFactory.build_update_task_value_event(
        task_id=str(task_id),
        value=1000
    )

    app.handle_event(event)

    aggregate = app.get_task_aggregate(task_id=task_id)

    assert aggregate.task.value == 1000
    write_model_mock.assert_called()


def test_task_manager_app_when_handling_add_evidence_event(
        write_model_mock,
        task_manager_app_testable,
        new_task_event_evidence_required
):
    app = task_manager_app_testable

    task_id = app.handle_event(new_task_event_evidence_required)

    evidence_event = TaskManagerAppEventFactory.build_add_evidence_event(
        task_id=str(task_id),
        data=b'This is Test Data'
    )

    app.handle_event(evidence_event)

    aggregate = app.get_task_aggregate(task_id=task_id)

    assert aggregate.task.evidence_data == b'This is Test Data'
    write_model_mock.assert_called()
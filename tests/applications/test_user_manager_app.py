import datetime
from unittest.mock import patch
from uuid import UUID

import pytest
from boe.applications.user_domain_apps import (
    UserManagerApp,
    UserAccountTypeEnum,
    UserManagerAppEventFactory
)
from pytest import fixture
from eventsourcing.application import AggregateNotFound


@fixture
def metric_publisher_mock():
    with patch("boe.applications.user_domain_apps.ServiceMetricPublisher", autospec=True) as client_mock:
        yield client_mock


@fixture
def write_model_mock():
    with patch("boe.applications.user_domain_apps.UserDomainWriteModel") as client_mock:
        yield client_mock


@fixture
def query_model_mock():
    with patch("boe.lib.domains.user_domain.UserDomainQueryModel", autospec=True) as client_mock:
        yield client_mock


@fixture
def notification_worker_client_mock():
    with patch("boe.applications.user_domain_apps.NotificationWorkerClient", autospec=True) as client_mock:
        yield client_mock


@fixture
def aws_cognito_mock():
    with patch("boe.applications.user_domain_apps.add_new_user_basic", autospec=True) as cognito_mock:
        yield cognito_mock


@fixture
def pika_client_mock():
    with patch("boe.applications.user_domain_apps.PikaPublisherClient", autospec=True) as client_mock:
        yield client_mock


@fixture
def family_uuid():
    return UUID("43f7858bbf9240258c8428e422bd3a28")


@fixture
def user_manager_app():
    return UserManagerApp()


@fixture
def create_family_local_event(family_uuid):
    return UserManagerAppEventFactory.build_create_family_local_event(
        family_id=str(family_uuid),
        account_type=UserAccountTypeEnum.adult.value,
        family_name='test_family',
        first_name='test_name',
        last_name='test_name',
        dob=datetime.datetime(month=9, day=10, year=1980).isoformat(),
        password='TEST_PASSWORD',
        email='test@email.com',
        desired_username='my_username'
    )


@fixture
def create_local_user_event(family_uuid):
    return UserManagerAppEventFactory.build_create_local_user_event(
        family_id=str(family_uuid),
        account_type=UserAccountTypeEnum.adult.value,
        first_name='test_name',
        last_name='test_name',
        dob=datetime.datetime(month=9, day=10, year=1980).isoformat(),
        password='TEST_PASSWORD',
        desired_username='my_username'
    )


def test_user_manager_app_when_handling_create_family_local_user_event(
        write_model_mock,
        pika_client_mock,

        user_manager_app,
        create_family_local_event
):
    testable = user_manager_app
    testable.handle_event(create_family_local_event)

    write_model_mock.assert_called()
    pika_client_mock.assert_called()


def test_user_manager_app_when_handling_create_local_user_event(
        write_model_mock,
        pika_client_mock,
        create_local_user_event,
        create_family_local_event,
        user_manager_app
):
    testable = user_manager_app

    testable.handle_event(create_family_local_event)
    testable.handle_event(create_local_user_event)
    write_model_mock.assert_called()
    pika_client_mock.assert_called()


def test_user_manager_app_when_handling_create_local_user_event_fails_missing_family_id(
        write_model_mock,
        pika_client_mock,
        create_local_user_event,
        create_family_local_event,
        user_manager_app
):
    testable = user_manager_app
    with pytest.raises(AggregateNotFound):
        testable.handle_event(create_local_user_event)
    write_model_mock.assert_called()
    pika_client_mock.assert_called()

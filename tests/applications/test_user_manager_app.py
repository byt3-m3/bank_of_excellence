import datetime
from unittest.mock import patch
from uuid import UUID

from boe.applications.user_domain_apps import (
    UserManagerApp,
    NewFamilyEvent,
    UserAccountTypeEnum,
    SubscriptionTypeEnum,
    UserManagerAppEventFactory
)
from pytest import fixture


@fixture
def metric_publisher_mock():
    with patch("boe.applications.user_domain_apps.ServiceMetricPublisher") as client_mock:
        yield client_mock


@fixture
def write_model_mock():
    with patch("boe.applications.user_domain_apps.UserDomainWriteModel") as client_mock:
        yield client_mock


@fixture
def notification_worker_client_mock():
    with patch("boe.applications.user_domain_apps.NotificationWorkerClient") as client_mock:
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
        password_hash=b'TEST_PASSWORD',
        email='test@email.com',
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

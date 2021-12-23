import datetime
from unittest.mock import patch
from uuid import UUID

from boe.applications.user_domain_apps import (
    UserManagerApp,
    NewFamilyEvent,
    SubscriptionTypeEnum,
    UserManagerAppEventFactory
)
from pytest import fixture


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
def family_uuid():
    return UUID("43f7858bbf9240258c8428e422bd3a28")


@fixture
def user_manager_app_testable():
    return UserManagerApp()


@fixture
def new_family_subscription_change_event(family_uuid):
    return UserManagerAppEventFactory.build_family_subscription_change_event(
        family_id=family_uuid,
        subscription_type=SubscriptionTypeEnum.premium
    )


@fixture
def new_child_account_event(family_uuid):
    return UserManagerAppEventFactory.build_new_child_account_event(
        family_id=family_uuid,
        first_name='TEST_NAME',
        last_name='TEST_NAME',
        email='TEST_EMAIL',
        age=7,
        grade=2,
        dob=datetime.datetime(month=12, day=20, year=2014)
    )


@fixture
def new_family_app_event_basic():
    return UserManagerAppEventFactory.build_new_family_event(
        description='TEST_DESCRIPTION',
        name='TEST_NAME',
        subscription_type=SubscriptionTypeEnum.basic
    )


@fixture
def new_family_app_event_premium():
    return NewFamilyEvent(
        description='TEST_DESCRIPTION',
        name='TEST_NAME',
        subscription_type=SubscriptionTypeEnum.premium
    )


def test_user_manager_app_when_handling_new_family_app_event(
        notification_worker_client_mock,
        write_model_mock,
        user_manager_app_testable,
        new_family_app_event_basic
):
    app = user_manager_app_testable
    event = new_family_app_event_basic

    result = app.handle_new_family_event(event=event)
    assert isinstance(result, UUID)

    write_model_mock.assert_called()
    notification_worker_client_mock.assert_called()


def test_user_manager_app_when_handling_new_child_account_event(
        aws_cognito_mock,
        notification_worker_client_mock,
        write_model_mock,
        user_manager_app_testable,
        new_family_app_event_basic
):
    app = user_manager_app_testable
    new_family_event = new_family_app_event_basic

    aggregate_id = app.handle_new_family_event(event=new_family_event)

    new_child_account_event = UserManagerAppEventFactory.build_new_child_account_event(
        family_id=str(aggregate_id),
        dob=datetime.datetime(month=12, day=20, year=2014),
        grade=2,
        email='test_email',
        first_name='test_firstname',
        last_name='test_lastname'
    )

    app.handle_new_child_account_event(event=new_child_account_event)

    write_model_mock.assert_called()
    notification_worker_client_mock.assert_called()
    aws_cognito_mock.assert_called()


def test_user_manager_app_when_handling_family_subscription_change_event(
        notification_worker_client_mock,
        write_model_mock,
        user_manager_app_testable,
        new_family_app_event_basic
):
    app = user_manager_app_testable
    new_family_event = new_family_app_event_basic

    aggregate_id = app.handle_new_family_event(event=new_family_event)

    sub_change_event = UserManagerAppEventFactory.build_family_subscription_change_event(
        family_id=str(aggregate_id),
        subscription_type=SubscriptionTypeEnum.premium
    )

    app.handle_family_subscription_type_change_event(event=sub_change_event)

    write_model_mock.assert_called()
    notification_worker_client_mock.assert_called()

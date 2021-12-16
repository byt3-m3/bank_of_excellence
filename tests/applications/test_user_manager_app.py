import datetime
from uuid import UUID

from boe.applications.user_manager_app import (
    UserManagerApp,
    NewFamilyEvent,
    SubscriptionTypeEnum,
    NewChildAccountEvent
)

from boe.lib.domains.user_domain import (
 UserAccountEntity
)
from pytest import fixture


@fixture
def user_manager_app_testable():
    return UserManagerApp()


@fixture
def new_child_account_event():
    return NewChildAccountEvent(
        family_id=UUID("22d3057e84424584b81f2a5d8b54319c"),
        first_name='TEST_NAME',
        last_name='TEST_NAME',
        email='TEST_EMAIL',
        age=7,
        grade=2,
        dob=datetime.datetime(month=12, day=20, year=2014)
    )


@fixture
def new_family_app_event_basic():
    return NewFamilyEvent(
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
        user_manager_app_testable,
        new_family_app_event_basic
):
    app = user_manager_app_testable
    event = new_family_app_event_basic

    result = app.handle_new_family_event(event=event)
    assert isinstance(result, UUID)


def test_user_manager_app_when_handling_new_child_account_event(
        user_manager_app_testable,
        new_child_account_event
):
    app = user_manager_app_testable
    event = new_child_account_event

    app.handle_new_child_account_event(event=event)

    account = app.get_user_account(family_id=event.family_id, account_id=UUID("0886360ea49a40b1b0f8e0d58079a316"))
    assert isinstance(account, UserAccountEntity)

from pytest import fixture
from boe.lib.domains.user_domain import (
    UserAccountAggregate,
    UserDomainFactory,
    AdultAccountDetail,
    UserAccountTypeEnum,
    ChildAccountDetail
)
from datetime import datetime


@fixture
def adult_account_testable() -> UserAccountAggregate:
    return UserDomainFactory.build_adult_account(
        first_name='TEST',
        last_name='TEST',
        email='TEST'
    )


@fixture
def child_account_testable() -> UserAccountAggregate:
    return UserDomainFactory.build_child_account(
        first_name='TEST',
        last_name='TEST',
        email='TEST',
        age=7,
        dob=datetime(year=2014, month=12, day=20),
        grade=7
    )


def test_adult_account_when_created(adult_account_testable):
    account = adult_account_testable

    assert account.account_type is UserAccountTypeEnum.adult
    assert isinstance(account.account_detail, AdultAccountDetail)


def test_child_account_when_created(child_account_testable):
    account = child_account_testable

    assert account.account_type is UserAccountTypeEnum.child
    assert isinstance(account.account_detail, ChildAccountDetail)

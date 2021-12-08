import pytest
from pytest import fixture
from boe.lib.domains.user_domain import (
    FamilyAggregate,
    UserAccountAggregate,
    SubscriptionTypeEnum,
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


@fixture
def family_testable(uuid4_1) -> FamilyAggregate:
    return UserDomainFactory.rebuild_family(
        _id=uuid4_1,
        name='TEST',
        members=[],
        description='TEST',
        subscription_type=SubscriptionTypeEnum.premium
    )


def test_adult_account_when_created(adult_account_testable):
    account = adult_account_testable

    assert account.account_type is UserAccountTypeEnum.adult
    assert isinstance(account.account_detail, AdultAccountDetail)


def test_child_account_when_created(child_account_testable):
    account = child_account_testable

    assert account.account_type is UserAccountTypeEnum.child
    assert isinstance(account.account_detail, ChildAccountDetail)


def test_family_when_created(family_testable):
    family = family_testable

    assert family.subscription_type is SubscriptionTypeEnum.premium


def test_family_when_adding_members(family_testable, child_account_testable, adult_account_testable):
    family = family_testable
    child_member = child_account_testable
    adult_member = adult_account_testable

    family.add_member(member=child_member)
    family.add_member(member=adult_member)

    assert len(family.members) == 2


def test_family_when_fetching_members(family_testable, child_account_testable):
    family = family_testable
    child_member = child_account_testable

    family.add_member(child_member)

    expectation = family.get_member(member_id=child_member.id)

    assert isinstance(expectation, UserAccountAggregate)
    assert expectation.account_type is UserAccountTypeEnum.child


def test_family_when_fetching_member_is_invalid(family_testable, child_account_testable):
    family = family_testable
    child_member = child_account_testable

    with pytest.raises(ValueError):
        family.get_member(member_id=child_member.id)

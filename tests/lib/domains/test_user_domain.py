from datetime import datetime
from uuid import UUID

import pytest
from boe.lib.domains.user_domain import (
    FamilyEntity,
    UserAccountEntity,
    SubscriptionTypeEnum,
    UserDomainFactory,
    UserDomainWriteModel,
    UserDomainQueryModel,
    UserDomainRepository,
    FamilyUserAggregate
)
from boe.utils.serialization_utils import serialize_dataclass_to_dict
from pytest import fixture


@fixture
def family_aggregate_dict():
    return {
        "_id": UUID("8882518b-8866-4474-9264-ce920dff8acf"),
        "family": {
            "id": UUID("8882518b-8866-4474-9264-ce920dff8acf"),
            "name": "TEST_NAME",
            "description": "TEST_DESCRIPTION",
            "subscription_type": 0
        },
        "member_map": {
            "1f939a5c-d622-43ae-87f2-ce7625ab9947": {
                "id": UUID("1f939a5c-d622-43ae-87f2-ce7625ab9947"),
                "account_type": {},
                "account_detail": {
                    "first_name": "test_firstname",
                    "last_name": "test_lastname",
                    "email": "test_email",
                    "dob": datetime.now(),
                    "age": 7,
                    "grade": 2
                }
            }
        },
        "version": 2
    }


@fixture
def family_user_aggregate():
    return UserDomainFactory.build_user_family_user_aggregate(
        description='TEST_DESCRIPTION',
        name="TEST_FAMILY",
        subscription_type=SubscriptionTypeEnum.basic
    )


@fixture
def user_domain_write_model() -> UserDomainWriteModel:
    return UserDomainWriteModel()


@fixture
def user_domain_repository() -> UserDomainRepository:
    return UserDomainRepository()


@fixture
def user_domain_query_model() -> UserDomainQueryModel:
    return UserDomainQueryModel()


@fixture
def adult_account_testable(uuid4_3) -> UserAccountEntity:
    return UserDomainFactory.rebuild_adult_account(
        first_name='TEST',
        last_name='TEST',
        email='TEST',
        _id=uuid4_3
    )


@fixture
def child_account_testable(uuid4_4) -> UserAccountEntity:
    return UserDomainFactory.rebuild_child_account(
        first_name='TEST',
        last_name='TEST',
        email='TEST',
        age=7,
        dob=datetime(year=2014, month=12, day=20),
        grade=7,
        _id=uuid4_4
    )


@fixture
def family_testable(uuid4_1) -> FamilyEntity:
    return UserDomainFactory.rebuild_family(
        _id=uuid4_1,
        name='TEST',
        members=[],
        description='TEST',
        subscription_type=SubscriptionTypeEnum.premium
    )


def test_family_user_aggregate_when_create(family_user_aggregate):
    aggregate: FamilyUserAggregate = family_user_aggregate

    assert aggregate.id == aggregate.family.id
    assert isinstance(aggregate.member_map, dict)


def test_family_user_aggregate_when_adding_member(family_user_aggregate, adult_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=adult_account_testable)

    assert len(aggregate.pending_events) == 2
    assert len(aggregate.member_map) == 1


def test_family_user_aggregate_when_adding_member_duplicate(family_user_aggregate, adult_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=adult_account_testable)
    with pytest.raises(ValueError):
        aggregate.add_family_member(user_account=adult_account_testable)


def test_family_user_aggregate_when_removing_member(family_user_aggregate, adult_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=adult_account_testable)
    aggregate.remove_family_member(user_id=adult_account_testable.id)

    assert len(aggregate.pending_events) == 3
    assert len(aggregate.member_map) == 0


def test_family_user_aggregate_when_changing_subscription_type(family_user_aggregate):
    aggregate: FamilyUserAggregate = family_user_aggregate

    assert aggregate.family.subscription_type is SubscriptionTypeEnum.basic
    aggregate.change_subscription_type(subscription_type=SubscriptionTypeEnum.premium)

    assert aggregate.family.subscription_type is SubscriptionTypeEnum.premium


def test_family_user_aggregate_when_creating_new_adult_member(family_user_aggregate):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.create_new_adult_member(
        first_name='TEST_NAME',
        last_name='LAST_NAME',
        email='TEST@EMAIL.COM'
    )

    assert len(aggregate.member_map) == 1


def test_family_user_aggregate_when_creating_new_child_member(family_user_aggregate):
    aggregate: FamilyUserAggregate = family_user_aggregate

    aggregate.create_new_child_member(
        first_name='TEST_NAME',
        last_name='LAST_NAME',
        email='TEST@EMAIL.COM',
        age=5,
        dob=datetime(year=2014, month=12, day=20),
        grade=5
    )

    assert len(aggregate.member_map) == 1


def _test_family_user_aggregate_when_rebuilding_from_dict(family_aggregate_dict):
    aggregate = FamilyUserAggregate.from_dict(data=family_aggregate_dict)

    print(aggregate)


def test_family_user_aggregate_when_serializing(family_user_aggregate):
    aggregate = family_user_aggregate

    aggregate.create_new_adult_member(
        first_name='TEST_NAME',
        last_name='LAST_NAME',
        email='TEST@EMAIL.COM'
    )
    aggregate_dict = serialize_dataclass_to_dict(family_user_aggregate)

    assert aggregate.id == aggregate_dict.get("family")['id']
    assert aggregate.family.subscription_type.value == aggregate_dict.get("family")['subscription_type']

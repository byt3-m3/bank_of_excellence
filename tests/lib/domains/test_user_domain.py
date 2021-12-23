from base64 import b64encode
from datetime import datetime
from uuid import UUID

import pytest
from boe.lib.domains.user_domain import (
    FamilyEntity,
    SubscriptionTypeEnum,
    UserDomainFactory,
    UserDomainWriteModel,
    UserDomainQueryModel,
    FamilyUserAggregate,
    UserAccount,
    Credential,
    CredentialTypeEnum,
    UserAccountTypeEnum
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
def child_member_account_testable(family_user_aggregate):
    return UserDomainFactory.build_user_account(
        account_type=UserAccountTypeEnum.child,
        first_name='TEST_NAME',
        last_name="TEST_LAST",
        family_id=family_user_aggregate.id,
        grade=2,
        email='test@mail.com',
        dob=datetime(year=2014, day=20, month=12)
    )


@fixture
def user_domain_write_model() -> UserDomainWriteModel:
    return UserDomainWriteModel()


@fixture
def user_domain_query_model() -> UserDomainQueryModel:
    return UserDomainQueryModel()


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
    assert isinstance(aggregate.members, list)


def test_family_user_aggregate_when_adding_child_member(family_user_aggregate, child_member_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=child_member_account_testable)

    for member in aggregate.members:
        assert isinstance(member, UserAccount)

    assert len(aggregate.pending_events) == 2
    assert len(aggregate.members) == 1


def test_family_user_aggregate_when_adding_member_duplicate(family_user_aggregate, child_member_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=child_member_account_testable)
    with pytest.raises(ValueError):
        aggregate.add_family_member(user_account=child_member_account_testable)


def test_family_user_aggregate_when_removing_member(family_user_aggregate, child_member_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate
    aggregate.add_family_member(user_account=child_member_account_testable)
    aggregate.remove_family_member(user_id=child_member_account_testable.id)

    assert len(aggregate.pending_events) == 3
    assert len(aggregate.members) == 0


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
        email='TEST@EMAIL.COM',
        dob=datetime(year=1988, month=9, day=6)
    )

    assert len(aggregate.members) == 1


def test_family_user_aggregate_when_creating_new_child_member(family_user_aggregate):
    aggregate: FamilyUserAggregate = family_user_aggregate

    aggregate.create_new_child_member(
        first_name='TEST_NAME',
        last_name='LAST_NAME',
        email='TEST@EMAIL.COM',
        dob=datetime(year=2014, month=12, day=20),
        grade=5
    )
    # print(aggregate.members[0].credential.creds.username)
    assert len(aggregate.members) == 1

    assert aggregate.members[0].credential.creds.username == ''


def test_family_user_aggregate_when_serializing(family_user_aggregate):
    aggregate = family_user_aggregate

    aggregate.create_new_adult_member(
        first_name='TEST_NAME',
        last_name='LAST_NAME',
        email='TEST@EMAIL.COM',
        dob=datetime(year=1988, month=9, day=6)
    )
    aggregate_dict = serialize_dataclass_to_dict(family_user_aggregate)

    assert aggregate.id == aggregate_dict.get("family")['id']
    assert aggregate.family.subscription_type.value == aggregate_dict.get("family")['subscription_type']


def test_family_user_aggregate_when_adding_creds(family_user_aggregate, child_member_account_testable):
    aggregate: FamilyUserAggregate = family_user_aggregate

    aggregate.add_family_member(user_account=child_member_account_testable)
    aggregate.set_basic_credential(member_id=child_member_account_testable.id,
                                   password_hash=b64encode("TEST_PASSWORD".encode()))

    assert aggregate.members[0].credential == Credential(
        credential_type=CredentialTypeEnum.basic,
        creds={'password_hash': b'VEVTVF9QQVNTV09SRA==', 'username': 'test_name_test_last'}
    )

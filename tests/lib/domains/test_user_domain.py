import uuid
from datetime import datetime

import pytest
from boe.lib.domains.user_domain import (

    SubscriptionTypeEnum,
    UserAccountAggregate,
    UserDomainFactory,
    UserDomainWriteModel,
    UserDomainQueryModel,
    FamilyAggregate,

    UserAccountTypeEnum
)
from pytest import fixture
from unittest.mock import patch


@fixture()
def add_item_utils_mock():
    with patch("boe.lib.domains.user_domain.add_item", autospec=True) as mock:
        yield mock


@fixture()
def update_item_utils_mock():
    with patch("boe.lib.domains.user_domain.update_item", autospec=True) as mock:
        yield mock


@fixture()
def get_item_utils_mock():
    with patch("boe.lib.domains.user_domain.get_item", autospec=True) as mock:
        yield mock


@fixture
def user_account_aggregate_w_local_credentials_adult(family_aggregate):
    return UserDomainFactory.build_user_account_aggregate_w_local_credential(
        account_type=UserAccountTypeEnum.adult,
        first_name='john',
        last_name='doe',
        username='john_doe',
        family_id=family_aggregate.id,
        password_hash=b'fake_password',
        email='test@gamil.com',
        dob=datetime(month=9, day=15, year=1970)
    )


@fixture
def user_account_aggregate_w_local_credentials_child(family_aggregate):
    return UserDomainFactory.build_user_account_aggregate_w_local_credential(
        account_type=UserAccountTypeEnum.child,
        first_name='jane',
        last_name='doe',
        username='jane_doe',
        family_id=family_aggregate.id,
        password_hash=b'fake_password',
        email='test@gamil.com',
        dob=datetime(month=9, day=15, year=2015)
    )


@fixture
def family_aggregate(

):
    return UserDomainFactory.build_family_aggregate(
        description='TEST_DESCRIPTION',
        name="TEST_FAMILY",
        subscription_type=SubscriptionTypeEnum.basic,
        _id=uuid.uuid4(),
        members=[

        ]
    )


@fixture
def child_member_account_testable(family_user_aggregate):
    return UserDomainFactory.build_user_account_entity(
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


def test_user_account_aggregate_when_created_adult(user_account_aggregate_w_local_credentials_adult):
    testable = user_account_aggregate_w_local_credentials_adult

    assert testable.user_entity.account_type is UserAccountTypeEnum.adult
    assert isinstance(testable, UserAccountAggregate)


def test_user_account_aggregate_when_created_child(user_account_aggregate_w_local_credentials_child):
    testable = user_account_aggregate_w_local_credentials_child

    assert testable.user_entity.account_type is UserAccountTypeEnum.child
    assert isinstance(testable, UserAccountAggregate)


def test_user_account_aggregate_when_updating_token(user_account_aggregate_w_local_credentials_adult):
    testable = user_account_aggregate_w_local_credentials_adult
    testable.update_local_credential_access_token(token=b'NEW_TOKEN')

    assert len(testable.pending_events) == 2
    assert testable.credential.access_token == b'NEW_TOKEN'


def test_user_account_aggregate_when_updating_password(user_account_aggregate_w_local_credentials_adult):
    testable = user_account_aggregate_w_local_credentials_adult
    testable.update_local_credential_password(password_hash=b'NEW_PASSWORD')

    assert len(testable.pending_events) == 2
    assert testable.credential.password_hash == b'NEW_PASSWORD'


def test_family_aggregate_when_created(family_aggregate):
    testable = family_aggregate

    assert isinstance(testable, FamilyAggregate)


def test_family_aggregate_when_adding_accounts(
        family_aggregate,
        user_account_aggregate_w_local_credentials_adult,
        user_account_aggregate_w_local_credentials_child
):
    testable = family_aggregate

    testable.add_family_member(
        user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
    )

    testable.add_family_member(
        user_aggregate_id=user_account_aggregate_w_local_credentials_child.id
    )

    assert testable.is_member(
        member_id=user_account_aggregate_w_local_credentials_adult.id
    ) is True

    assert testable.is_member(
        member_id=user_account_aggregate_w_local_credentials_child.id
    ) is True

    assert len(testable.members) == 2


def test_family_aggregate_when_adding_duplicate_accounts(
        family_aggregate,
        user_account_aggregate_w_local_credentials_adult
):
    testable = family_aggregate

    testable.add_family_member(
        user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
    )

    with pytest.raises(ValueError):
        testable.add_family_member(
            user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
        )


def test_family_aggregate_when_changing_subscription(
        family_aggregate
):
    assert family_aggregate.family.subscription_type is SubscriptionTypeEnum.basic

    family_aggregate.change_family_subscription(subscription=SubscriptionTypeEnum.premium)

    assert family_aggregate.family.subscription_type is SubscriptionTypeEnum.premium


def test_user_domain_write_model_when_saving_family_aggregate(
        add_item_utils_mock,
        family_aggregate,
        user_account_aggregate_w_local_credentials_adult,
        user_domain_write_model
):
    family_aggregate.add_family_member(user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id)
    user_domain_write_model.save_aggregate(family_aggregate)


def test_user_domain_write_model_when_saving_user_account_aggregate(
        add_item_utils_mock,
        family_aggregate,
        user_account_aggregate_w_local_credentials_adult,
        user_domain_write_model
):
    user_domain_write_model.save_aggregate(family_aggregate)
    user_domain_write_model.save_aggregate(user_account_aggregate_w_local_credentials_adult)


def test_user_domain_query_model_when_fetching_family_by_id(
        add_item_utils_mock,
        get_item_utils_mock,
        user_domain_query_model,
        user_domain_write_model,
        user_account_aggregate_w_local_credentials_adult,
        family_aggregate
):
    family_aggregate.add_family_member(
        user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
    )
    user_domain_write_model.save_aggregate(family_aggregate)

    results = user_domain_query_model.get_family_by_id(family_aggregate_id=family_aggregate.id)

    get_item_utils_mock.assert_called()
    # assert isinstance(results, user_domain_query_model.BasicFamilyModel)


def test_user_domain_query_model_when_fetching_user_account_by_id(
        add_item_utils_mock,
        get_item_utils_mock,
        user_domain_query_model,
        user_domain_write_model,
        user_account_aggregate_w_local_credentials_adult,
        family_aggregate
):
    user_domain_write_model.save_aggregate(user_account_aggregate_w_local_credentials_adult)

    results = user_domain_query_model.get_user_account_by_id(
        user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
    )
    get_item_utils_mock.assert_called()
    # assert isinstance(results, user_domain_query_model.UserAccountModel)


def test_user_domain_query_model_when_fetching_local_user_credentials(
        add_item_utils_mock,
        get_item_utils_mock,
        user_domain_query_model,
        user_domain_write_model,
        user_account_aggregate_w_local_credentials_adult,
        family_aggregate
):
    user_domain_write_model.save_aggregate(user_account_aggregate_w_local_credentials_adult)

    results = user_domain_query_model.get_user_local_credentials_by_id(
        user_aggregate_id=user_account_aggregate_w_local_credentials_adult.id
    )
    get_item_utils_mock.assert_called()
    # assert isinstance(results, user_domain_query_model.LocalCredentialModel)

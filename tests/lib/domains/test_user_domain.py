import pytest
from pytest import fixture
from boe.lib.domains.user_domain import (
    FamilyAggregate,
    UserAccountAggregate,
    SubscriptionTypeEnum,
    UserDomainFactory,
    AdultAccountDetail,
    UserAccountTypeEnum,
    UserDomainWriteModel,
    UserDomainQueryModel,
    UserDomainRepository,
    ChildAccountDetail
)
from datetime import datetime
from uuid import UUID


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


def _test_user_domain_write_model_when_saving_user_account(adult_account_testable, child_account_testable):
    # TODO: Needs Mocks

    child_account = child_account_testable
    adult_account = adult_account_testable

    write_model = UserDomainWriteModel()

    write_model.save_user_account(account=child_account)
    write_model.save_user_account(account=adult_account)


def _test_user_domain_query_model_when_querying_by_account_id(user_domain_query_model):
    # TODO: Needs Mocks

    account_id = UUID("4afbadc5-6522-4890-819e-fa003027280f")

    query_model = user_domain_query_model

    model_dict = query_model.get_family_by_id(agg_id=account_id)
    print(model_dict)


def _test_user_domain_repository_when_querying_by_account_id(user_domain_repository):
    # TODO: Needs Mocks

    account_id = UUID("4afbadc5-6522-4890-819e-fa003027280f")

    repo = user_domain_repository

    model = repo.get_user_account(account_id=account_id)
    print(model)


def _test_user_domain_query_model_when_scan_user_table(user_domain_query_model):
    # TODO: Needs Mocks

    query_model = user_domain_query_model

    items = query_model.scan_user_accounts()
    print(items)


def _test_user_domain_repository_when_getting_all_accounts(user_domain_repository):
    # TODO: Needs Mocks

    repo = user_domain_repository

    accounts = repo.get_user_accounts()
    print(accounts)


def _test_user_domain_write_model_when_saving_family(family_testable, user_domain_write_model):
    # TODO: Needs Mocks

    family = family_testable
    write_model = user_domain_write_model

    result = write_model.save_family(family=family)
    print(result)


def _test_user_domain_query_model_when_querying_family(user_domain_query_model):
    query_model = user_domain_query_model

    query_model.get_family_by_id(family_id=UUID("184abb3f-be96-471c-8e18-f3b479939492"))


def _test_user_domain_repository_when_querying_family(user_domain_repository):
    repo = user_domain_repository
    model = repo.get_family(family_id=UUID("184abb3f-be96-471c-8e18-f3b479939492"))
    print(model)


def _test_user_domain_query_model_when_scanning_family(user_domain_query_model):
    query_model = user_domain_query_model

    items = query_model.scan_families()
    print(items)


def _test_user_domain_repo_when_scanning_family(user_domain_repository):
    repo = user_domain_repository

    models = repo.get_families()
    print(models)

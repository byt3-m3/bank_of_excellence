from uuid import UUID, uuid4

import pytest
from boe.lib.domains.bank_domain import (
    BankAccountEntity,
    BankTransactionMethodEnum,
    BankTransactionEntity,
    BankDomainWriteModel,
    BankDomainAggregate,
    BankDomainFactory,
    BankDomainRepository,
    BankTransactionValueObject,
    BankAccountStateEnum
)
from pytest import fixture


@fixture
def bank_domain_write_model():
    return BankDomainWriteModel()


@fixture
def bank_domain_repository():
    return BankDomainRepository()


@fixture
def bank_account_entity_testable(bank_account_uuid) -> BankAccountEntity:
    return BankDomainFactory.rebuild_bank_account_entity(
        _id=bank_account_uuid,
        owner_id=bank_account_uuid,
        is_overdraft_protected=False,
        balance=0,
        state=BankAccountStateEnum.enabled,

    )


@fixture
def bank_transaction_entity_add_testable(bank_account_uuid, item_uuid) -> BankTransactionEntity:
    return BankDomainFactory.build_bank_transaction_entity(
        account_id=bank_account_uuid,
        item_id=item_uuid,
        method=BankTransactionMethodEnum.add,
        value=100.00
    )


@fixture
def bank_transaction_entity_subtract_testable(bank_account_uuid, item_uuid_2) -> BankTransactionEntity:
    return BankDomainFactory.build_bank_transaction_entity(
        account_id=bank_account_uuid,
        item_id=item_uuid_2,
        method=BankTransactionMethodEnum.subtract,
        value=10.00
    )


@fixture
def bank_domain_aggregate_testable(
        bank_account_uuid
) -> BankDomainAggregate:
    return BankDomainFactory.build_bank_domain_aggregate(
        owner_id=bank_account_uuid,
        is_overdraft_protected=True
    )


@fixture
def bank_domain_aggregate_no_transactions_testable(
        bank_account_entity_testable
) -> BankDomainAggregate:
    return BankDomainAggregate(
        bank_account=bank_account_entity_testable,
        bank_transactions=[

        ]
    )


@fixture
def bank_domain_aggregate_empty_testable(
        bank_account_entity_testable
) -> BankDomainAggregate:
    return BankDomainAggregate(
        bank_account=bank_account_entity_testable,
        bank_transactions=[

        ]
    )


def test_bank_account_aggregate_when_created(bank_domain_aggregate_testable):
    aggregate: BankDomainAggregate = bank_domain_aggregate_testable
    assert aggregate.id == aggregate.bank_account.id


def test_bank_account_aggregate_when_calculating_account_balance(
        bank_domain_aggregate_testable,
        bank_transaction_entity_add_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_testable

    aggregate.apply_transaction_to_account(bank_transaction_entity_add_testable)
    balance = aggregate.calculate_account_balance()

    assert balance == 100


def test_bank_account_aggregate_when_applying_transaction(
        bank_domain_aggregate_no_transactions_testable,
        bank_transaction_entity_add_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable
    transaction: BankTransactionEntity = bank_transaction_entity_add_testable

    aggregate.apply_transaction_to_account(transaction=transaction)

    assert len(aggregate.pending_events) == 2
    assert aggregate.bank_account.balance == 100


def test_bank_account_aggregate_when_applying_transaction_fails(
        bank_domain_aggregate_no_transactions_testable,
        bank_transaction_entity_add_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable
    transaction: BankTransactionEntity = bank_transaction_entity_add_testable

    bad_uuid = UUID("00000000-0000-0000-0000-000000000099")
    transaction.account_id = bad_uuid
    with pytest.raises(ValueError):
        aggregate.apply_transaction_to_account(transaction=transaction)


def test_bank_account_aggregate_when_new_transaction(
        bank_domain_aggregate_empty_testable,
        bank_account_entity_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_empty_testable

    assert aggregate.version == 1

    aggregate.new_transaction(
        account_id=bank_account_entity_testable.owner_id,
        item_id=uuid4(),
        method=BankTransactionMethodEnum.add,
        value=10

    )

    assert aggregate.bank_account.balance == 10
    assert aggregate.bank_account.id == bank_account_entity_testable.id
    assert len(aggregate.pending_events) == 2
    assert aggregate.version == 2


def test_bank_account_aggregate_when_disable_account(
        bank_domain_aggregate_no_transactions_testable,
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable

    aggregate.disable_account()

    assert aggregate.bank_account.state is BankAccountStateEnum.disabled


def test_bank_account_aggregate_when_enable_account(
        bank_domain_aggregate_no_transactions_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable

    aggregate.disable_account()
    aggregate.enable_account()

    assert aggregate.bank_account.state is BankAccountStateEnum.enabled


def test_bank_account_aggregate_when_fetching_transaction(
        bank_domain_aggregate_testable,
        bank_transaction_entity_add_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_testable
    transaction: BankTransactionEntity = bank_transaction_entity_add_testable
    aggregate.apply_transaction_to_account(transaction=transaction)
    _transaction = aggregate.get_transaction_by_id(transaction_id=transaction.id)

    assert isinstance(_transaction, BankTransactionValueObject)


def test_bank_account_aggregate_when_fetching_transaction_fails(
        bank_domain_aggregate_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_testable
    with pytest.raises(ValueError):
        aggregate.get_transaction_by_id(transaction_id=uuid4())

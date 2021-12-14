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
        bank_account_entity_testable,
        bank_transaction_entity_add_testable,
        bank_transaction_entity_subtract_testable
) -> BankDomainAggregate:
    return BankDomainAggregate(
        bank_accounts=[
            bank_account_entity_testable
        ],
        bank_transactions=[
            bank_transaction_entity_add_testable,
            bank_transaction_entity_subtract_testable
        ]
    )


@fixture
def bank_domain_aggregate_no_transactions_testable(
        bank_account_entity_testable
) -> BankDomainAggregate:
    return BankDomainAggregate(
        bank_accounts=[
            bank_account_entity_testable
        ],
        bank_transactions=[

        ]
    )


@fixture
def bank_domain_aggregate_empty_testable(

) -> BankDomainAggregate:
    return BankDomainAggregate(
        bank_accounts=[

        ],
        bank_transactions=[

        ]
    )


def test_bank_account_aggregate_when_calculating_account_balance(bank_domain_aggregate_testable, bank_account_uuid):
    aggregate = bank_domain_aggregate_testable
    balance = aggregate.calculate_account_balance(account_id=bank_account_uuid)

    assert balance == 90.0


def test_bank_account_aggregate_when_applying_transaction(
        bank_domain_aggregate_no_transactions_testable,
        bank_account_uuid,
        bank_transaction_entity_add_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable
    transaction: BankTransactionEntity = bank_transaction_entity_add_testable

    aggregate.apply_transaction_to_account(transaction=transaction)

    account_entity = aggregate.get_bank_account_entity(entity_id=bank_account_uuid)
    assert len(aggregate.pending_events) == 2
    assert account_entity.balance == 100


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


def test_bank_account_aggregate_when_creating_new_account(bank_domain_aggregate_empty_testable, bank_account_uuid_2):
    aggregate: BankDomainAggregate = bank_domain_aggregate_empty_testable

    aggregate.new_bank_account(
        owner_id=bank_account_uuid_2,
        is_overdraft_protected=True
    )

    account = aggregate.get_bank_account_entity(entity_id=bank_account_uuid_2)

    assert isinstance(account, BankAccountEntity)
    assert len(aggregate.bank_accounts) == 1


def test_bank_account_aggregate_when_new_transaction(
        bank_domain_aggregate_empty_testable,
        bank_account_entity_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_empty_testable

    aggregate.new_bank_account(
        owner_id=bank_account_entity_testable.owner_id,
        is_overdraft_protected=bank_account_entity_testable.is_overdraft_protected
    )

    assert aggregate.version == 2

    aggregate.new_transaction(
        account_id=bank_account_entity_testable.owner_id,
        item_id=uuid4(),
        method=BankTransactionMethodEnum.add,
        value=10

    )

    account = aggregate.get_bank_account_entity(entity_id=bank_account_entity_testable.owner_id)

    assert account.balance == 10
    assert account.id == bank_account_entity_testable.id
    assert len(aggregate.pending_events) == 3
    assert aggregate.version == 3


def test_bank_account_aggregate_when_disable_account(
        bank_domain_aggregate_no_transactions_testable,
        bank_account_entity_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable

    aggregate.disable_account(account_id=bank_account_entity_testable.id)
    account = aggregate.get_bank_account_entity(entity_id=bank_account_entity_testable.id)

    assert account.state is BankAccountStateEnum.disabled


def test_bank_account_aggregate_when_enable_account(
        bank_domain_aggregate_no_transactions_testable,
        bank_account_entity_testable
):
    aggregate: BankDomainAggregate = bank_domain_aggregate_no_transactions_testable

    aggregate.disable_account(account_id=bank_account_entity_testable.id)
    aggregate.enable_account(account_id=bank_account_entity_testable.id)

    account = aggregate.get_bank_account_entity(entity_id=bank_account_entity_testable.id)

    assert account.state is BankAccountStateEnum.enabled

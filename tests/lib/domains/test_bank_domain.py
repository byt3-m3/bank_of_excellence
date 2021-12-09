from pytest import fixture
from boe.lib.domains.bank_domain import (
    BankAccountAggregate,
    BankTransactionMethodEnum,
    BankTransaction,
    BankDomainWriteModel,
    BankDomainQueryModel,
    BankDomainFactory,
    BankDomainRepository,
    BankAccountStateEnum
)
from uuid import uuid4, UUID


@fixture
def bank_domain_repository():
    return BankDomainRepository()


@fixture
def bank_account_testable(uuid4_1) -> BankAccountAggregate:
    return BankDomainFactory.rebuild_bank_account(
        _id=uuid4_1,
        owner_id=uuid4_1,
        is_overdraft_protected=False,
        _balance=0,
        state=BankAccountStateEnum.active,
        transactions=[]
    )


@fixture
def bank_transaction_add_testable(uuid4_2) -> BankTransaction:
    return BankDomainFactory.build_bank_transaction(
        item_id=uuid4_2,
        method=BankTransactionMethodEnum.add,
        value=5.00
    )


@fixture
def bank_transaction_subtract_testable(uuid4_3) -> BankTransaction:
    return BankDomainFactory.build_bank_transaction(
        item_id=uuid4_3,
        method=BankTransactionMethodEnum.subtract,
        value=5.00
    )


def test_bank_account_when_created(bank_account_testable):
    bank_account = bank_account_testable

    assert bank_account.balance == 0
    assert bank_account.owner_id == bank_account.id
    assert bank_account.is_overdraft_protected is False


def test_bank_account_when_adding_transaction(bank_account_testable, bank_transaction_add_testable):
    bank_account = bank_account_testable
    transaction = bank_transaction_add_testable

    bank_account.apply_transaction(transaction=transaction)

    assert bank_account.balance == 5.0
    assert len(bank_account.transactions) == 1
    assert isinstance(bank_account.state, BankAccountStateEnum)
    for transaction in bank_account.transactions:
        assert isinstance(transaction.method, BankTransactionMethodEnum)


def test_bank_account_when_subtracting_transaction(bank_account_testable, bank_transaction_subtract_testable):
    bank_account = bank_account_testable
    transaction = bank_transaction_subtract_testable

    bank_account.apply_transaction(transaction=transaction)
    assert bank_account.balance == -5.0
    assert len(bank_account.transactions) == 1
    for transaction in bank_account.transactions:
        assert isinstance(transaction.method, BankTransactionMethodEnum)


def test_bank_account_when_fetching_transaction(bank_account_testable, bank_transaction_subtract_testable):
    bank_account = bank_account_testable
    transaction = bank_transaction_subtract_testable

    bank_account.apply_transaction(transaction=transaction)
    assert bank_account.balance == -5.0
    assert len(bank_account.transactions) == 1

    transaction_result = bank_account.get_transaction_by_id(transaction_id=transaction.transaction_id)
    assert transaction_result is transaction


def test_bank_account_when_new_transaction(bank_account_testable):
    bank_account = bank_account_testable

    bank_account.new_transaction(
        item_id=uuid4(),
        method=BankTransactionMethodEnum.add,
        value=150
    )

    assert bank_account.balance == 150
    assert len(bank_account.transactions) == 1


def test_bank_account_when_validating_transaction_count(bank_account_testable, bank_transaction_add_testable):
    bank_account = bank_account_testable
    transaction_1 = bank_transaction_add_testable
    bank_account.apply_transaction(
        transaction=transaction_1
    )
    assert bank_account.transaction_count == 1


def _test_bank_domain_write_model_when_saving_bank_account(bank_account_testable, bank_transaction_add_testable):
    # TODO: Add Mock for WriteModel to Mongo

    write_model = BankDomainWriteModel()
    bank_account_testable.apply_transaction(transaction=bank_transaction_add_testable)
    write_model.save_bank_account(
        bank_account=bank_account_testable
    )


def _test_bank_domain_query_model_when_querying_by_id(uuid_1):
    # TODO: Add Mock for Query
    query_model = BankDomainQueryModel()

    data = query_model.get_bank_account_by_id(account_id=UUID("fccd9dbf-0138-4a93-bd60-0cb69269875f"))

    model = BankDomainFactory.rebuild_bank_account(
        **data
    )

    assert isinstance(model, BankAccountAggregate)
    for transaction in model.transactions:
        assert isinstance(transaction, BankTransaction)


def _test_bank_domain_repo_when_saving_bank_account(bank_domain_repository, bank_account_testable):
    # TODO: Add Mock for Query
    repo = bank_domain_repository
    bank_account = bank_account_testable
    repo.save_bank_account(account=bank_account)


def _test_bank_domain_repo_when_fetching_bank_account(bank_domain_repository):
    # TODO: Add Mock for Query
    repo = bank_domain_repository
    result = repo.get_bank_account(account_id=UUID("184abb3f-be96-471c-8e18-f3b479939492"))
    print(result)

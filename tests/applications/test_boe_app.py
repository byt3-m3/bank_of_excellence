from uuid import uuid4

from boe.applications import (
    BankManagerApp,
    EstablishNewAccountEvent
)
from boe.lib.domains.bank_domain import BankDomainAggregate
from pytest import fixture


@fixture
def establish_new_account_event(user_account_uuid):
    return EstablishNewAccountEvent(
        owner_id=uuid4(),
        is_overdraft_protected=True
    )


@fixture
def bank_manager_app_testable():
    return BankManagerApp()


def _test_basic_test(bank_manager_app_testable):
    app = bank_manager_app_testable

    app.test_event()


def test_bank_manager_app_when_handle_establish_new_account_event(
        bank_manager_app_testable,
        establish_new_account_event
):
    app = bank_manager_app_testable
    event = establish_new_account_event
    _id = app.handle_establish_new_account_event(event=event)

    aggregate = app.repository.get(_id)
    assert isinstance(aggregate, BankDomainAggregate)

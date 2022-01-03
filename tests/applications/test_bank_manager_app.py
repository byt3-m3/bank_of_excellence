from unittest.mock import patch
from uuid import uuid4

from boe.applications.bank_domain_apps import (
    BankManagerApp,
    BankDomainAppEventFactory
)
from boe.lib.domains.bank_domain import (

    BankDomainAggregate,
    BankTransactionMethodEnum
)
from pytest import fixture


@fixture
def metric_publisher_mock():
    with patch("boe.applications.bank_domain_apps.ServiceMetricPublisher") as client_mock:
        yield client_mock


@fixture
def write_model_mock():
    with patch("boe.applications.bank_domain_apps.BankDomainWriteModel") as client_mock:
        yield client_mock


@fixture
def notification_worker_client_mock():
    with patch("boe.applications.bank_domain_apps.NotificationWorkerClient") as client_mock:
        yield client_mock


@fixture
def establish_new_account_event(user_account_uuid):
    return BankDomainAppEventFactory.build_establish_new_account_event(
        owner_id=str(uuid4()),
        is_overdraft_protected=True
    )


@fixture
def bank_manager_app_testable():
    return BankManagerApp()


def _test_basic_test(bank_manager_app_testable):
    app = bank_manager_app_testable

    app.test_event()


def test_bank_manager_app_when_handle_establish_new_account_event(
        metric_publisher_mock,
        write_model_mock,
        notification_worker_client_mock,
        bank_manager_app_testable,
        establish_new_account_event
):
    app = bank_manager_app_testable
    event = establish_new_account_event
    _id = app.handle_event(event)

    aggregate = app.repository.get(_id)
    assert isinstance(aggregate, BankDomainAggregate)
    write_model_mock.assert_called()
    notification_worker_client_mock.assert_called()
    metric_publisher_mock.assert_called()


def test_bank_manager_app_when_handling_new_transaction_event(
        metric_publisher_mock,
        write_model_mock,
        notification_worker_client_mock,
        bank_manager_app_testable,
        establish_new_account_event,
):
    app = bank_manager_app_testable

    new_account_event = establish_new_account_event
    transaction_event = BankDomainAppEventFactory.build_new_transaction_event(
        account_id=str(new_account_event.owner_id),
        item_id=str(uuid4()),
        value=6,
        transaction_method=BankTransactionMethodEnum.add
    )

    app.handle_event(new_account_event)
    aggregate_id = app.handle_event(transaction_event)
    aggregate = app.repository.get(aggregate_id=aggregate_id)

    assert isinstance(aggregate, BankDomainAggregate)
    assert aggregate.bank_account.balance == 6
    write_model_mock.assert_called()
    notification_worker_client_mock.assert_called()
    metric_publisher_mock.assert_called()

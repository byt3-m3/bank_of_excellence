from boe.applications import BankManagerApp

from pytest import fixture


@fixture
def bank_manager_app_testable():
    return BankManagerApp()


def test_basic_test(bank_manager_app_testable):
    app = bank_manager_app_testable

    app.test_event()

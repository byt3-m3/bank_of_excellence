from unittest.mock import patch
from uuid import UUID

from boe.lib.domains.persistence_domain import PersistenceDomainFactory
from pytest import fixture


@fixture
def bank_domain_write_model_mock():
    with patch("boe.lib.domains.persistence_domain.BankDomainWriteModel") as write_model_mock:
        yield write_model_mock


@fixture
def persistence_aggregate_testable(set_persistence_test_env):
    return PersistenceDomainFactory.build_persistence_aggregate(
        aggregate_id=UUID('eaaa7901-e49a-4bbd-ab64-410e061d7339'),
        aggregate_type='BankDomainAggregate'

    )


def test_persistence_aggregate_when_created(persistence_aggregate_testable):
    aggregate = persistence_aggregate_testable
    assert len(aggregate.pending_events) == 1
    assert aggregate.record.aggregate_id == UUID('eaaa7901-e49a-4bbd-ab64-410e061d7339')


def test_persistence_aggregate_when_persisting_bank_aggregate(
        bank_domain_write_model_mock,
        persistence_aggregate_testable

):
    aggregate = persistence_aggregate_testable

    payload = {
        "bank_account": {
            "id": "eaaa7901-e49a-4bbd-ab64-410e061d7339",
            "owner_id": "eaaa7901-e49a-4bbd-ab64-410e061d7339",
            "is_overdraft_protected": False,
            "state": 0,
            "balance": 0
        },
        "bank_transactions": [],
        "version": 1
    }

    aggregate.persist_bank_aggregate(payload=payload)

    bank_domain_write_model_mock.assert_called()
    assert len(aggregate.pending_events) == 2

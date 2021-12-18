from uuid import UUID

from boe.lib.domains.persistence_domain import PersistenceDomainFactory
from pytest import fixture


@fixture
def persistence_aggregate_testable(set_persistence_test_env):
    return PersistenceDomainFactory.build_persistence_aggregate(
        aggregate_id=UUID('eaaa7901-e49a-4bbd-ab64-410e061d7339')
    )


def _test_persistence_aggregate_when_adding_new_request(persistence_aggregate_testable):
    aggregate = persistence_aggregate_testable

    aggregate.new_persistence_request(payload={"data": "data"}, payload_type='TestType')

    print(aggregate.pending_events)


def test_persistence_aggregate_when_persisting_bank_aggregate(persistence_aggregate_testable):
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

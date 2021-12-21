from boe.applications.persistence_domain_apps import (
    PersistenceServiceApp,
    PersistenceDomainAppEventFactory,
    PersistBankDomainAggregateEvent
)
from pytest import fixture
from boe.lib.domains.bank_domain import BankDomainFactory

@fixture
def persistence_service_app_testable(set_persistence_test_env):
    return PersistenceServiceApp()


@fixture
def persist_bank_domain_aggregate_event() -> PersistBankDomainAggregateEvent:
    return PersistenceDomainAppEventFactory.build_persist_bank_domain_aggregate_event(
        aggregate_id="ce09e314-d378-4dd3-a133-41fcd14cef56",
        payload={"Test": "Test"},
        payload_type="TestPayload"
    )


def _test_persistence_service_app_when_handling_persist_bank_domain_agg_event(
    persistence_service_app_testable,
    persist_bank_domain_aggregate_event
):
    app = persistence_service_app_testable
    event = persist_bank_domain_aggregate_event

    bank_account_agg = BankDomainFactory.build_bank_domain_aggregate(owner_id=uuid4(), is_overdraft_protected=False)

    app.handle_persist_bank_domain_aggregate(event=event)

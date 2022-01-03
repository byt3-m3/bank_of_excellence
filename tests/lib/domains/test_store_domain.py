from unittest.mock import patch

from boe.lib.domains.store_domain import (
    StoreDomainFactory,
    StoreDomainQueryModel
)
from pytest import fixture
from uuid import UUID

@fixture
def store_domain_query_model_testable():
    return StoreDomainQueryModel()


@fixture
def store_item_entity():
    return StoreDomainFactory.build_store_item_entity(
        value=5.00,
        name="ScreenTime",
        description='TEST_DESCRIPTION'
    )


@fixture
def store_aggregate_testable(uuid4_4):
    return StoreDomainFactory.build_store_aggregate(
        family_id=uuid4_4
    )


def test_store_aggregate_when_creating_new_item(store_aggregate_testable):
    aggregate = store_aggregate_testable

    store_item = StoreDomainFactory.build_store_item_entity(
        name='TV Time',
        value=10,
        description='TV time for your kid'
    )

    aggregate.new_store_item(
        store_item=store_item
    )

    assert len(aggregate.store_items) == 1
    assert len(aggregate.pending_events) == 2


def test_store_aggregate_when_removing_store_item(store_aggregate_testable):
    aggregate = store_aggregate_testable
    store_item = StoreDomainFactory.build_store_item_entity(
        name='TV Time',
        value=10,
        description='TV time for your kid'
    )

    aggregate.new_store_item(
        store_item=store_item
    )

    item_ids = aggregate.store_item_ids
    for item_id in item_ids:
        aggregate.remove_store_item(item_id=item_id)

    assert len(aggregate.store_items) == 0
    assert len(aggregate.pending_events) == 3


def test_store_domain_write_model_when_saving_aggregate(store_aggregate_testable):
    store_aggregate = store_aggregate_testable

    store_item_1 = StoreDomainFactory.build_store_item_entity(
        name='TV Time',
        value=10,
        description='TV time for your kid'
    )

    store_item_2 = StoreDomainFactory.build_store_item_entity(
        name='IPAD Time',
        value=6,
        description='IPAD time for your kid'
    )

    store_aggregate.new_store_item(
        store_item=store_item_1
    )
    store_aggregate.new_store_item(
        store_item=store_item_2
    )

    with patch("boe.lib.domains.store_domain.StoreDomainWriteModel") as model_mock:
        write_model = model_mock()
        write_model.save_store_aggregate(aggregate=store_aggregate)
        model_mock.assert_called()


def test_query_model_when_fetching_store(store_domain_query_model_testable):

    query_model = store_domain_query_model_testable

    query_model.get_store_by_id(store_id=UUID("9a44e287-f167-4c41-a715-74f4a3e40bab"))
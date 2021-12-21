from uuid import uuid4
from unittest.mock import patch
from boe.applications.store_domain_apps import StoreManagerApp, StoreManagerAppEventFactory
from pytest import fixture


@fixture
def store_domain_write_model_mock():
    pass
    with patch("boe.applications.store_domain_apps.StoreDomainWriteModel") as write_model_mock:
        yield write_model_mock


@fixture
def store_manager_app_testable():
    return StoreManagerApp()


@fixture
def new_store_event():
    return StoreManagerAppEventFactory.build_new_store_event(
        family_id=str(uuid4())
    )


def test_store_manager_app_when_handling_new_store_event(
        store_domain_write_model_mock,
        store_manager_app_testable,
        new_store_event
):
    app = store_manager_app_testable
    event = new_store_event

    app.handle_new_store_event(event=event)
    store_domain_write_model_mock.assert_called()


def test_store_manager_app_when_handling_new_store_item_event(
        store_domain_write_model_mock,
        store_manager_app_testable,
        new_store_event
):
    app = store_manager_app_testable
    store_id = app.handle_new_store_event(event=new_store_event)

    new_store_item_event = StoreManagerAppEventFactory.build_new_store_item_event(
        store_id=str(store_id),
        item_name='TEST_NAME',
        item_description="TEST_DESC",
        item_value=100
    )

    app.handle_new_store_item_event(event=new_store_item_event)
    store_domain_write_model_mock.assert_called()


def test_store_manager_app_when_handling_remove_store_item_event(
        store_domain_write_model_mock,
        store_manager_app_testable,
        new_store_event
):
    app = store_manager_app_testable
    store_id = app.handle_new_store_event(event=new_store_event)

    new_store_item_event = StoreManagerAppEventFactory.build_new_store_item_event(
        store_id=str(store_id),
        item_name='TEST_NAME',
        item_description="TEST_DESC",
        item_value=100
    )
    app.handle_new_store_item_event(event=new_store_item_event)

    store = app.get_store(aggregate_id=store_id)

    assert len(store.store_item_ids) == 1

    for item_id in store.store_item_ids:
        remove_store_item_event = StoreManagerAppEventFactory.build_remove_store_item_event(
            store_id=str(store_id),
            item_id=str(item_id)
        )
        app.handle_remove_store_item_event(event=remove_store_item_event)

    store = app.get_store(aggregate_id=store_id)
    assert len(store.store_item_ids) == 0

    store_domain_write_model_mock.assert_called()

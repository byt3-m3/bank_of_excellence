import pytest
from cbaxter1988_utils.pagination_utils import BasePaginator, BasePage


@pytest.fixture
def items():
    return [
        {"test": "test"},
        {"test": "test1"},
        {"test": "test2"},
        {"test": "test3"},
        {"test": "test4"},
        {"test": "test5"},
        {"test": "test6"},
        {"test": "test7"},
        {"test": "test8"},
        {"test": "test9"},
        {"test": "test10"},
    ]


def test_base_paginator(number_list):
    """
    Tests the creation of pages with items

    :param number_list:
    :return:
    """
    # Set Up
    page_items_expectation = [4, 5, 6]
    page_count_expectation = 3

    paginator = BasePaginator()

    # invocation
    paginator.make_pages(items=number_list, page_size=3)
    page = paginator.get_page(page_number=2)

    # Validation
    assert isinstance(page, BasePage)
    assert paginator.page_count == page_count_expectation
    assert page.items == page_items_expectation


def test_base_pagiation(items):
    # Set Up
    paginator = BasePaginator()
    page_items_expectation = [{'test': 'test'}, {'test': 'test1'}]
    page_count_expectation = 6

    # Invocation
    paginator.make_pages(items=items, page_size=2)
    page = paginator.get_page(page_number=1)

    # Validation
    assert isinstance(page, BasePage)
    assert page.items == page_items_expectation
    assert paginator.page_count == page_count_expectation

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List

"""
A Collection of tools that can be used for handling Pagination. 

"""


class IBasePage(ABC):
    """
    Interface for BasePage
    """

    @abstractmethod
    def add_item(self, item: Any):
        pass


class IPaginator(ABC):
    """
    Interface for Pagniator

    """

    @abstractmethod
    def add_page(self, item: IBasePage):
        pass

    @abstractmethod
    def get_page(self, page_number: int):
        pass


@dataclass()
class BasePage(IBasePage):
    """
    Basic Page
    """
    page_id: int
    items: List[Any]
    next_page: int
    previous_page: int
    item_count: int

    def __post_init__(self):
        self.next_page = self.page_id + 1
        self.previous_page = self.page_id - 1
        if self.previous_page == 0:
            self.previous_page = 1

    @staticmethod
    def make_pages(items: List[Any], page_size: int, sort: bool = True, reverse: bool = True) -> List['BasePage']:
        try:
            if sort:
                items.sort()
        except TypeError:
            pass

        if reverse:
            items.reverse()

        page_count = round(len(items) / page_size)

        pages = []
        for i in range(page_count):
            i += 1
            page_items = []
            for idx in range(len(items)):

                if len(page_items) < page_size:
                    page_items.append(items.pop())

            page = BasePage(
                page_id=i,
                items=page_items,
                next_page=0,
                previous_page=0,
                item_count=page_size
            )
            pages.append(page)

        return pages

    def add_item(self, item: Any):
        pass

    def get_page(self, page_number: int):
        pass


class BasePaginator(IPaginator):
    """
    Basic Paginator that can be used to create pages
    """

    def __init__(self, **kwargs):
        self._page_map = {}
        self._page_list = []

        self._active_page = None
        self._total_pages = None
        self.total_records = 0

    def _check_page_map_list(self):
        if len(self._page_list) == len(self._page_map.keys()):
            return True
        else:
            return False

    def add_page(self, page: BasePage):
        """
        Adds new page to paginator

        :param page:
        :return:
        """
        if self._check_page_map_list():
            self._page_map[page.page_id] = page
            self._page_list.append(page)
            return True
        else:
            print(f"Unable to add page {page}")
            return False

    def remove_page(self, page_id: int):
        """
        Removes page from paginator

        :param page_id:
        :return:
        """
        page = self._page_map[page_id]
        self._page_list.remove(page)
        del self._page_map[page_id]

    def add_pages(self, pages: List[BasePage]):
        _ = [
            self.add_page(page=page)
            for page in pages
        ]

    def get_page(self, page_number: int) -> BasePage:
        return self._page_map[page_number]

    def make_pages(self, items: List[Any], page_size: int, reverse: bool = True, sort: bool = True):
        pages = BasePage.make_pages(
            items=items,
            page_size=page_size,
            reverse=reverse,
            sort=sort,
        )
        self.add_pages(pages=pages)
        return self

    @property
    def pages(self):
        return self._page_list

    @property
    def page_count(self):
        if len(self._page_map.keys()) == len(self.pages):
            return len(self.pages)

    def paginate(self):
        cur_page = 0
        total_pages = 10
        while cur_page <= total_pages:
            pass

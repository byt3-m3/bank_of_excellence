from copy import deepcopy

from typing import List, Any

"""
Collection of random  utilities 
"""


def check_list_len(items: List[Any], expected_len: int) -> bool:
    """
    Checks the length of the given list

    :param items: List of any type of objects.
    :param expected_len: the expected length of the list.
    :return:
    """
    if len(items) == expected_len:
        return True
    else:
        return False


def clone_object(item: Any) -> Any:
    """
    Creates a copy of the given item.

    :param item: Any object expected to be cloned
    :return:
    """
    return deepcopy(item)

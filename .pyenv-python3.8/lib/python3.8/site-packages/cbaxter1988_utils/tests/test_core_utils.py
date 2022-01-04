from cbaxter1988_utils.core_utils import clone_object, check_list_len


def test_clone_object(person):
    new_object = clone_object(person)
    assert id(person) != id(new_object)


def test_check_list_len(number_list):
    result = check_list_len(items=number_list, expected_len=10)
    assert result is True

def assert_value_equals(value1, value2):
    assert value1 == value2


def assert_is_instance(testable, expected_instance):
    assert isinstance(testable, expected_instance)


def assert_is_subclass(testable, expected_class):
    assert issubclass(type(testable), expected_class)


def assert_len_eq(testable, expected_len):
    assert len(testable) == expected_len

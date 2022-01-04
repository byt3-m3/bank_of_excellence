from cbaxter1988_utils.auth_utils import (
    generate_random_password_basic,
    generate_random_password_advanced,
    make_advanced_password_policy,
    make_basic_password_policy
)

from pytest import fixture


@fixture
def basic_password_policy():
    return make_basic_password_policy(
        length=8
    )


@fixture
def advanced_password_policy():
    return make_advanced_password_policy(
        length=8,
        digits_count=1,
        upper_case_count=1,
        lower_case_count=1,
        special_characters_count=2,
        alphabets_count=1
    )


def test_generate_random_password_basic(
        basic_password_policy
):
    pw = generate_random_password_basic(
        password_policy=basic_password_policy
    )
    assert len(pw) == 8


def test_generate_random_password_advanced(
        advanced_password_policy
):
    pw = generate_random_password_advanced(
        password_policy=advanced_password_policy

    )

    assert len(pw) >= 8

from unittest.mock import patch

from cbaxter1988_utils.aws_cognito_utils import add_new_user_basic, list_user_pools, delete_user
from pytest import fixture


@fixture
def aws_client_mock():
    with patch("cbaxter1988_utils.aws_cognito_utils.get_cognito_idp_client") as client_mock:
        yield client_mock


@fixture
def test_user_name():
    return 'test_user'


@fixture
def test_user_pool_id():
    return 'us-east-1_fRkg83NZI'


@fixture
def test_user_email():
    return 'cbaxtertech@gmail.com'


def test_add_new_user(
        aws_client_mock,
        test_user_name,
        test_user_email,
        test_user_pool_id
):
    add_new_user_basic(
        pool_id=test_user_pool_id,
        user_email=test_user_email,
        username=test_user_name
    )

    aws_client_mock.assert_called()


def test_delete_user(
        aws_client_mock,
        test_user_pool_id,
        test_user_name
):
    delete_user(pool_id=test_user_pool_id, username=test_user_name)
    aws_client_mock.assert_called()


def test_list_user_pools(aws_client_mock):
    list_user_pools()

    aws_client_mock.assert_called()

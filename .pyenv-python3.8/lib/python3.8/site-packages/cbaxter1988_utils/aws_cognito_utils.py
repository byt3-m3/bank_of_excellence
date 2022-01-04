from cbaxter1988_utils.auth_utils import (
    generate_random_password_advanced,
    make_advanced_password_policy
)
from cbaxter1988_utils.aws_utils import get_cognito_idp_client
from cbaxter1988_utils.log_utils import get_logger

logger = get_logger(__name__)


def add_new_user_basic(
        pool_id: str,
        username: str,
        user_email: str,
        temp_password_len: int = 8,
        temp_password_alphabets_count: int = 1,
        temp_password_digits_count: int = 1,
        temp_password_special_characters_count: int = 1,
        temp_password_upper_case_count: int = 1,
        temp_password_lower_case_count: int = 1,
):
    """
    This function Creates a new pool user for the specified UserPool.

    This function only uses the 'email' UserAttributes when creating the user.



    :param pool_id: ID of the AWS cognito Pool
    :param username: Desired username
    :param user_email: User email address
    :param temp_password_len:
    :param temp_password_alphabets_count:
    :param temp_password_digits_count:
    :param temp_password_special_characters_count:
    :param temp_password_upper_case_count:
    :param temp_password_lower_case_count:
    :return:
    """
    client = get_cognito_idp_client()

    temp_password = generate_random_password_advanced(
        make_advanced_password_policy(
            length=temp_password_len,
            alphabets_count=temp_password_alphabets_count,
            digits_count=temp_password_digits_count,
            special_characters_count=temp_password_special_characters_count,
            upper_case_count=temp_password_upper_case_count,
            lower_case_count=temp_password_lower_case_count
        )
    )
    logger.info(f"Created Temp Password='{temp_password}' for '{user_email}'")
    return client.admin_create_user(
        UserPoolId=pool_id,
        Username=username,
        TemporaryPassword=temp_password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': user_email
            },
        ]
    )


def delete_user(pool_id: str, username: str):
    client = get_cognito_idp_client()
    result = client.admin_delete_user(
        UserPoolId=pool_id,
        Username=username
    )

    logger.info(f"Removed User='{username}' from UserPool={pool_id}")
    return result


def list_user_pools():
    client = get_cognito_idp_client()
    return client.list_user_pools(
        MaxResults=50
    )

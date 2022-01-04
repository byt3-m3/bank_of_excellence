import json

from cbaxter1988_utils.aws_utils import get_boto3_client


def get_secrets_manager_client():
    return get_boto3_client('secretsmanager')


def get_credentials(secret_name: str) -> dict:
    client = get_secrets_manager_client()
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']

        return json.loads(secret)

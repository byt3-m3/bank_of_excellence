import boto3
from cbaxter1988_utils.environment_utils import get_env

"""
Collection of Utilities interacting with the boto3 library

"""


def get_boto3_client(service):
    """
    Gets new boto3 client

    :param service: AWS service id, example: s3
    :return:
    """
    return boto3.client(
        service,
        region_name=get_env(key="AWS_DEFAULT_REGION"),
        aws_access_key_id=get_env(key="AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_env(key="AWS_SECRET_ACCESS_KEY")
    )


def get_event_bridge_client():
    """
    Returns EventBridge client.

    :return:
    """
    return get_boto3_client('events')


def get_lambda_client():
    """
    Returns EventBridge client.

    :return:
    """
    return get_boto3_client('lambda')


def get_s3_client():
    """
    Returns S3 client.

    :return:
    """
    return get_boto3_client(service="s3")


def get_dynamo_client():
    """
    Returns DynamoDB client.

    :return:
    """
    return get_boto3_client(service="dynamo")


def get_cloudwatch_client():
    """
    Returns Cloudwatch client.

    :return:
    """
    return get_boto3_client(service='cloudwatch')


def get_dynamo_table(table_id: str):
    """
    Returns DynamoDB table.

    :return:
    """
    resource = boto3.resource('dynamodb')

    return resource.Table(table_id)


def get_cognito_idp_client():
    return get_boto3_client('cognito-idp')

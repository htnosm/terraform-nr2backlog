import json
import os
import pytest
import boto3

from moto import mock_aws

# 環境変数を設定
os.environ['SECRET_NAME'] = 'dummy_secret_name'


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def secretsmanager(aws_credentials):
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="us-east-1")


@pytest.fixture(scope="function")
def secretsmanager_client(secretsmanager):
    secret_value = json.dumps({
        'BACKLOG_DOMAIN': 'example.backlog.com',
        'BACKLOG_API_KEY': 'dummy_api_key',
        'BACKLOG_PROJECT_ID': '1',
        'BACKLOG_ISSUE_TYPE_ID': '2',
        'BACKLOG_ISSUE_PRIORITY_ID': '3',
        'BACKLOG_ISSUE_ASSIGNEE_ID': '4',
        'BACKLOG_ISSUE_CLOSE_STATUS_ID': '5',
        'BACKLOG_ISSUE_NOTIFIED_USER_IDS': '1,2,3'
    })
    secretsmanager.create_secret(Name=os.environ['SECRET_NAME'], SecretString=secret_value)
    yield secretsmanager

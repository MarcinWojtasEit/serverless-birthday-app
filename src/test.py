import pytest
import boto3
import datetime
from birthday import *
from moto import mock_dynamodb

TABLENAME = "users"

@pytest.fixture
def use_moto():
    @mock_dynamodb
    def dynamodb_client():
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

        # Create the table
        dynamodb.create_table(
            TableName=TABLENAME,
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        return dynamodb
    return dynamodb_client

@mock_dynamodb
def test_put_user_item_status_ok(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth\": \"1995-10-12\"\n}",
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 204

@mock_dynamodb
def test_put_user_item_wrong_username(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth\": \"1995-10-12\"\n}",
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test123"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_date_after(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth\": \"2195-10-12\"\n}",
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_wrong_body(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth2\": \"1995-10-12\"\n}",
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_incorect_date(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth\": \"21ss95-10-12\"\n}",
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_incorect_method(use_moto):
    use_moto()
    event = {
        "body": "{\n\t\"dateOfBirth\": \"1995-10-12\"\n}",
        "httpMethod": "POST",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_none_body(use_moto):
    use_moto()
    event = {
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_put_user_item_empty_body(use_moto):
    use_moto()
    event = {
        "body": {},
        "httpMethod": "PUT",
        "pathParameters": {
            "username":"test"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_incorrect_date_in_databese(use_moto):
    use_moto()

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': "2220.20.14"
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"tom"
        },
    }
    return_data = handler(event, "")

    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_get_birthday_is_today_status_ok(use_moto):
    use_moto()

    today = datetime.datetime.today()

    dateOfBirth = datetime.datetime(
        today.year - 20, today.month, today.day
    )

    dateOfBirth = dateOfBirth.strftime("%Y-%m-%d")

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': dateOfBirth
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"tom"
        },
    }
    return_data = handler(event, "")

    assert return_data['statusCode'] == 200
    assert return_data['body'] == '"Hello, tom Happy birthday!"'

@mock_dynamodb
def test_get_birthday_is_not_today_status_ok(use_moto):
    use_moto()

    today = datetime.datetime.today()

    dateOfBirth = datetime.datetime(
        today.year - 10, today.month - 1, today.day - 2
    )

    dateOfBirth = dateOfBirth.strftime("%Y-%m-%d")

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': dateOfBirth
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"tom"
        },
    }
    return_data = handler(event, "")

    assert return_data['statusCode'] == 200
    assert return_data['body'] != '"Hello, tom Happy birthday!"'

@mock_dynamodb
def test_get_birthday_is_tomorrow_status_ok(use_moto):
    use_moto()

    today = datetime.datetime.today()

    dateOfBirth = datetime.datetime(
        today.year -10, today.month, today.day + 1
    )

    dateOfBirth = dateOfBirth.strftime("%Y-%m-%d")

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': dateOfBirth
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"tom"
        },
    }
    return_data = handler(event, "")

    assert return_data['statusCode'] == 200
    assert return_data['body'] == '"Hello, tom Your birthday is tomorrow"'

@mock_dynamodb
def test_get_birthday_wrong_username(use_moto):
    use_moto()

    today = datetime.datetime.today()

    dateOfBirth = datetime.datetime(
        today.year - 1, today.month - 1, today.day - 2
    )

    dateOfBirth = dateOfBirth.strftime("%Y-%m-%d")

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': dateOfBirth
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"tom111"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 400

@mock_dynamodb
def test_get_birthday_username_not_exist(use_moto):
    use_moto()

    today = datetime.datetime.today()

    dateOfBirth = datetime.datetime(
        today.year - 1, today.month - 1, today.day - 2
    )

    dateOfBirth = dateOfBirth.strftime("%Y-%m-%d")

    table = boto3.resource('dynamodb').Table(TABLENAME)
    table.put_item(
        Item={
            'username': 'tom',
            'dateOfBirth': dateOfBirth
        }
    )
    event = {
        "httpMethod": "GET",
        "pathParameters": {
            "username":"marcin"
        },
    }
    return_data = handler(event, "")
    assert return_data['statusCode'] == 404

def test_put_user_item_to_wrong_database(monkeypatch):
    # Setup
    envs = {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
    }
    monkeypatch.setattr(os, 'environ', envs)

    return_data = put_user_item("test", "1925-10-26")
    assert return_data['statusCode'] == 400
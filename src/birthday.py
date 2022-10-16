import json
import datetime
import boto3
import os

# Get environment variables
table_name = os.environ['TABLENAME']
aws_environment = os.environ['AWSENV']

def handler(event, context):
    username = event['pathParameters']['username']
    
    if not username.isalpha():
        return {
            "statusCode": 400,
            "body": json.dumps('%s must contain only letters.' % username)
        }

    method = event.get('httpMethod')

    if method == 'PUT':
        try:
            decodedBody = json.loads(event['body'])
            dateOfBirth = decodedBody['dateOfBirth']
            dateOfBirthDatatime = datetime.datetime.strptime(dateOfBirth, '%Y-%m-%d')

            if dateOfBirthDatatime > datetime.datetime.today():
                return {
                    "statusCode": 400,
                    "body": json.dumps('Must be a date before the today date.')
                }
        except TypeError:
            return {
                "statusCode": 400,
                "body": json.dumps('Body should contain dateOfBirth parameter')
            }
        except KeyError:
            return {
                "statusCode": 400,
                "body": json.dumps('Incorect body')
            }
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps('Incorrect data format, should be YYYY-MM-DD.')
            }

        return put_user_item(username,dateOfBirth)

    elif method == 'GET':
        return get_birthday_message(username)

    else:
        return {
            "statusCode": 400,
            "body": json.dumps('%s method is not supported' % method)
        }

def put_user_item(username,dateOfBirth):
    users_table = get_table()
    
    try:
        users_table.put_item(
           Item={
                'username': username,
                'dateOfBirth': dateOfBirth
            }
        )

        return {
            'statusCode': 204        
        }
    except:
        return {
            'statusCode': 400,
            'body': json.dumps('Error saving the data')
        }

def get_birthday_message(username):
    users_table = get_table()

    try:
        user = users_table.get_item(Key={"username": username})
        dateOfBirth = datetime.datetime.strptime(user["Item"]["dateOfBirth"], '%Y-%m-%d')
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps('Incorrect data format, should be YYYY-MM-DD.')
        }
    except KeyError:
        return {
            "statusCode": 404,
            "body": json.dumps('Username does not exist')
        }

    today = datetime.datetime.today()

    if(
        today.month == dateOfBirth.month
        and today.day == dateOfBirth.day
    ):
        return {
            "statusCode": 200,
            "body": json.dumps('Hello, %s Happy birthday!' % username)
        }
    elif(
        today.month == dateOfBirth.month
        and today.day >= dateOfBirth.day
        or today.month > dateOfBirth.month
    ):
        nextBirthDayYear = today.year + 1
    else:
        nextBirthDayYear = today.year

    nextBirthDay = datetime.datetime(
        nextBirthDayYear, dateOfBirth.month, dateOfBirth.day
    )

    diff = nextBirthDay - today
    
    if diff.days == 0:
        return {
            "statusCode": 200,
            "body": json.dumps('Hello, %s Your birthday is tomorrow' % username)
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps('Hello, %s Your birthday is in %d day(s)' % (username, diff.days))
        }


def get_table():
    if aws_environment == "AWS_SAM_LOCAL":
        dev_environment = os.environ['DEVENV']
        # SAM LOCAL
        if dev_environment == "OSX":
            # Environment ins Mac OSX
            users_table = boto3.resource('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000/").Table(table_name)

        elif dev_environment == "Windows":
            # Environment is Windows
            users_table = boto3.resource('dynamodb', endpoint_url="http://docker.for.windows.localhost:8000/").Table(table_name)

        else:
            # Environment is Linux
            users_table = boto3.resource('dynamodb', endpoint_url="http://127.0.0.1:8000").Table(table_name)
    else:
        # AWS
        users_table = boto3.resource('dynamodb').Table(table_name)

    return users_table
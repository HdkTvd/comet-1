import time
from os import urandom
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class User:
    def __init__(self, password: str, first_name: str, last_name: str, mobile, email: str):
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.mobile = int(mobile)
        self.email = email
        self.role = str()


class Student(User):
    def __init__(self, password: str, first_name: str, last_name: str, mobile, email: str, department: str, roll):
        super().__init__(password, first_name, last_name, mobile, email)
        self.department = department
        self.roll = int(roll)
        self.role = 'student'


class Admin(User):
    def __init__(self, username: str, password: str, first_name: str, last_name: str, mobile, email: str):
        super().__init__(password, first_name, last_name, mobile, email)
        self.username = username
        self.role = 'admin'


dynamodb = boto3.resource('dynamodb', region_name='ap-south-1', endpoint_url="http://localhost:8000")


class ADMINDB:
    def __init__(self):
        self.table = dynamodb.create_table(
            TableName='ADMINDB',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'password',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'first_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'last_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'mobile',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print("ADMINDB status:", self.table.table_status)

    def add(self, admin: Admin):
        self.table.put_item(
            Item={
                'username': admin.username,
                'password': admin.password,
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'mobile': admin.mobile,
                'email': admin.email
            }
        )

    def get(self, username: str, password: str):
        try:
            response = self.table.get_item(
                Key={
                    'username': username,
                    'password': password
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Item']
            print("GetItem succeeded:")
            return json.dumps(item, indent=4, cls=DecimalEncoder)


class STUDENTDB:
    def __init__(self):
        self.table = dynamodb.create_table(
            TableName='STUDENTDB',
            KeySchema=[
                {
                    'AttributeName': 'roll',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'password',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'first_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'last_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'mobile',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'department',
                    'AttributeType': 'S'
                }

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print("ADMINDB status:", self.table.table_status)

    def add(self, student: Student):
        self.table.put_item(
            Item={
                'roll': student.roll,
                'password': student.password,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'mobile': student.mobile,
                'email': student.email,
                'department': student.department
            }
        )

    def get(self, roll: str, password: str):
        try:
            response = self.table.get_item(
                Key={
                    'roll': roll,
                    'password': password
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            item = response['Item']
            print("GetItem succeeded:")
            return json.dumps(item, indent=4, cls=DecimalEncoder)


class Session:
    ticks_to_expire = 10800

    def __init__(self, user: User):
        self.key = urandom(6)
        self.user = user
        self.birth = time.time()
        self.expiry = self.birth + __class__.ticks_to_expire


class ActiveSessionArray:
    def __init__(self):
        self.sessions = dict()

    def add(self, session: Session):
        self.sessions[session.key] = session

    def validate(self, key):  # DANGEROUS : CAUTION
        if key in self.sessions.keys:
            if self.sessions[key].expiry <= time.time():
                del self.sessions[key]
                return 0
            else:
                return 1
        else:
            return -1

    def super_validate(self):  # expired session cleaner
        for key in [*self.sessions]:
            self.validate(key)


__all__ = ["User", "Student", "Admin", "Session", "ActiveSessionArray", "STUDENTDB", "ADMINDB"]

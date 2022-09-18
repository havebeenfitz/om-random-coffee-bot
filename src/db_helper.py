from collections import namedtuple
from typing import Optional
from src.vars import PROD
from src.models.user import User
from src.models.static_models import MeetingFormatCallback

import boto3
from boto3.dynamodb.conditions import Key, Attr


class DBHelper(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBHelper, cls).__new__(cls)
        return cls.instance

    _usersTable = boto3.resource('dynamodb').Table('users_prod' if PROD else 'users_debug')

    def get_user(self, user_id: str) -> Optional[User]:
        response = self._usersTable.get_item(
            Key={'user_id': str(user_id)}
        )

        if 'Item' in response:
            return User(response['Item'])
        else:
            return None

    def get_all_users(self) -> [User]:
        response = self._usersTable.scan(
            FilterExpression=Attr('is_paused').eq(False)
        )

        if 'Items' in response:
            users_response = response['Items']

            while 'LastEvaluatedKey' in response:
                response = self._usersTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                users_response.extend(response['Items'])

            return [User(user_dict=user) for user in users_response]
        else:
            return []

    def update_user_profile(
        self,
        user: User
    ):
        item = {
            'user_id': user.user_id,
            'username': user.username,
            'gender': user.gender,
            'format': user.meeting_format,
            'bio': user.bio,
            'is_paused': user.is_paused
        }
        if user.meeting_format == MeetingFormatCallback.offline:
            item['city'] = user.city
            item['country']: user.country

        self._usersTable.put_item(Item=item)

    def pause_user(self, should_pause: bool, user: User):
        self._usersTable.update_item(
            Key={
                'user_id': user.user_id
            },
            UpdateExpression='SET is_paused = :pause',
            ExpressionAttributeValues={
                ':pause': should_pause
            },
            ReturnValues="UPDATED_NEW"
        )

    def delete_user(self, user: User):
        self._usersTable.delete_item(
            Key={
                'user_id': user.user_id
            }
        )

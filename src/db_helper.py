from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key, Attr

from src.models.static_models import MeetingFormatCallback
from src.models.user import User
from src.vars import PROD


class DBHelper(object):
    def __new__(cls, override_prod: bool = False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBHelper, cls).__new__(cls)
        cls._usersTable = boto3.resource('dynamodb').Table(
            'users_prod' if override_prod else 'users_prod' if PROD else 'users_debug'
        )
        return cls.instance

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
        if user.meeting_format == MeetingFormatCallback.offline.id:
            item['city'] = user.city
            item['country'] = user.country

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

    def delete_user(self, user_id):
        self._usersTable.delete_item(
            Key={
                'user_id': str(user_id)
            }
        )

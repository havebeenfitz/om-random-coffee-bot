from typing import Optional
import boto3


class DBHelper(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBHelper, cls).__new__(cls)
        return cls.instance

    _usersTable = boto3.resource('dynamodb').Table('users')

    def get_all_users(self):
        response = self._usersTable.scan()
        users = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self._usersTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            users.extend(response['Items'])

        return users

    def update_user(
            self,
            user_id: str,
            username: str,
            gender: str,
            meeting_format: str,
            bio: str,
            country: Optional[str] = None,
            city: Optional[str] = None
    ):
        item = {
                'id': user_id,
                'username': username,
                'gender': gender,
                'format': meeting_format,
                'country': country,
                'city': city,
                'bio': bio
            }
        if city and country:
            item['city'] = city
            item['country'] = country

        self._usersTable.put_item(
            Item=item
        )

    def delete_user(self, user_id: str):
        self._usersTable.delete_item(
            Key={
                'id': user_id
            }
        )

from typing import Optional
import boto3


class DBHelper:
    _instance = None

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DBHelper, cls).__new__(cls)
        return cls._instance

    _usersTable = boto3.resource('dynamodb').Table('users')

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

from typing import Optional
import boto3


class DBHelper:

    users = boto3.resource('dynamodb').Table('users')

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

        self.users.put_item(
            Item=item
        )

    def delete_user(self, user_id: str):
        self.users.delete_item(
            Key={
                'id': user_id
            }
        )


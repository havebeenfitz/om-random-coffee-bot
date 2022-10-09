# Random Coffee Telegram Bot

![dogee](https://om-random-coffee-bot-bucket.s3.amazonaws.com/sobaka.jpg)

The bot generates pairs from registered users for them to meet each other either online or in person.


Deployed with AWS Lambda (python 3.9 runtime). User data stored in DynamoDB.

Dependencies:

- Python Telegram Bot
- Geonames sdk
- AWS sdk

## TODO:

### Priority:

- AWS cron job
  - Generate pairs weekly
  - Bot asks if a user contacted his/her pair on Wed/Thu
- ~~Inline Menu~~
  - ~~Pause/Resume buttons~~
  - ~~Generate pairs for admins~~
  - ~~Provide Feedback button + send to separate channel~~


### Nice to have:

- Select offline location from a list
- Notify members about the next round
- ~~Edit profile from inline menu~~
- Move all strings to a separate file/module

# Random Coffee Bot for OM community

![dogee](https://om-random-coffee-bot-bucket.s3.amazonaws.com/sobaka.jpg)

OM Random Coffee Telegram bot 

Deployed with AWS Lambda (python 3.9 runtime). 
User data stored in DynamoDB.

Dependencies:

- Python Telegram Bot
- Geonames sdk
- AWS sdk

## TODO:

### Priority:

- AWS cron job
  - Generate pairs weekly
  - Bot asks if a user contacted his/her pair on Wed/Thu
- Inline Menu
  - Pause/Resume buttons
  - Generate pairs for admins
  - Provide Feedback button + send to separate channel


### Nice to have:

- Select offline location from a list
- Notify members about the next round
- Edit profile from inline menu
- Move all strings to a separate file/module

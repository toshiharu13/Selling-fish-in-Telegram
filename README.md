# Selling-fish-in-Telegram
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![Elasticpath](./images/logo_4.png)](https://www.elasticpath.com/)
## Description
This telegram bot is an interface of online shop(elasticpath in our case) for example, a funny fish store
## How to install
Python3 should be already installed.
You have allready registered in [elasticpath](https://www.elasticpath.com/)

- clone project from [github.com](https://github.com)
```shell
git clone git@github.com:toshiharu13/Selling-fish-in-Telegram.git
```
- Install and run [Redis](https://realpython.com/python-redis/)
- Use `pip` to install dependencies:
```bash
pip install -r requirements.txt
```
- Create and fill in .env file: 
```dotenv
TELEGRAM_TOKEN = 'Telegram bot token '
```
```dotenv
ELASTICPATH = 'Your elasticpath_user_id'
```
## Starting bot
Just type:
```shell
python tel_bot.py
```
![fish_bot](./images/bot_screen.png)
Link to the Telegram bot: [@test_ork_bot](https://t.me/test_ork_bot)
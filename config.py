import os
from typing import List


BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')


API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = int(os.getenv('API_PORT', '8000'))


DATABASE_PATH = os.getenv('DATABASE_PATH', 'blog.db')


ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    print("Не установлен токен бота!")
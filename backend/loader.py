from dotenv import load_dotenv
from json import loads
from os import getenv
from aiogram import Bot, Dispatcher

# Получаем секретные данные с файла .env
load_dotenv()

ADMINS = loads(getenv('ADMINS'))  # список админов
BOT_ADDRESS = getenv('BOT_ADDRESS')  # адрес бота в ТГ
TOKEN = getenv('TOKEN')  # токен бота телеграм
SUPPORT = getenv('SUPPORT')

DB_USER = getenv('DB_USER')  # имя пользователя БД
DB_PASSWORD = getenv('DB_PASSWORD')  # пароль пользователя БД
DB_NAME = getenv('DB_NAME')  # название БД
DB_HOST = getenv('DB_HOST')  # хост БД
DB_PORT = getenv('DB_PORT')  # порт БД

URL = getenv('URL')  # ссылка на бэк
RABBIT_HOST = getenv('RABBIT_HOST')  # хост реббитмк

# ссылка для доступа к БД
DATABASE_URL = f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# экземпляры для работы с aiogram: клиент бота и диспетчер
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher()

# теги фастапи для документации сваггер
FASTAPI_TAGS = [
    {
        'name': 'Messages',
        'description': 'Messaging management.'
    },
    {
        'name': 'Client tasks',
        'description': 'Client task management.'
    },
    {
        'name': 'Freelancer tasks',
        'description': 'Freelancer task management.'
    },
    {
        'name': 'Client offers',
        'description': 'Client offer management.'
    },
    {
        'name': 'users',
        'description': 'API endpoints for managing users'
    }
]

# ключи для с3
S3_KEY_ID = getenv('S3_KEY_ID')
S3_SECRET_KEY = getenv('S3_SECRET_KEY')
S3_ENDPOINT_URL = getenv('S3_ENDPOINT_URL')

S3_BUCKET_NAME = getenv('S3_BUCKET_NAME', 'user-files')

REQUIRED_CHANNEL_ID = getenv('REQUIRED_CHANNEL_ID')
REQUIRED_CHANNEL_USERNAME = getenv('REQUIRED_CHANNEL_USERNAME')
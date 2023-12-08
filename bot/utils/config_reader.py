from environs import Env
from pathlib import Path

from pydantic.v1 import BaseSettings

# Получаем путь до директории главного файла main.py
BASE_DIR = Path(__file__).parent

# Используем экземпляр объекта.
env = Env()
# Читаем наш .env конфиг.
env.read_env(f'{BASE_DIR}/.env')


# Создаем класс, который будет хранить в себе данные из конфига.
class Config(BaseSettings):
    api_id: str
    api_hash: str

    blacklist_chat: str
    blacklist_en_chat: str

    postgres_pass: str
    postgres_user: str
    postgres_host: str
    postgres_db: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'


config = Config()

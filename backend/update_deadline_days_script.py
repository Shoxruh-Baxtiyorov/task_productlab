from os import getenv
from sqlalchemy import create_engine, text
import dotenv

dotenv.load_dotenv()

DB_USER = getenv('DB_USER')  # имя пользователя БД
DB_PASSWORD = getenv('DB_PASSWORD')  # пароль пользователя БД
DB_NAME = getenv('DB_NAME')  # название БД
DB_HOST = getenv('DB_HOST')  # хост БД
DB_PORT = getenv('DB_PORT')  # порт БД

DATABASE_URL = f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("UPDATE tasks SET deadline_days = deadline_days * 24 WHERE deadline_days IS NOT NULL;"))
    conn.execute(text("UPDATE contracts SET deadline_days = deadline_days * 24 WHERE deadline_days IS NOT NULL;"))
    conn.execute(text("UPDATE auto_responses SET deadline_days = deadline_days * 24 WHERE deadline_days IS NOT NULL;"))
    conn.execute(text("UPDATE offers SET deadline_days = deadline_days * 24 WHERE deadline_days IS NOT NULL;"))
    conn.commit()
    print("Данные deadline_days успешно обновлены во всех таблицах.")
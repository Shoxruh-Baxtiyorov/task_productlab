from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import loader

# Инициализируем engine для доступа к БД и создаем экземпляр sessionmaker,
# чтобы быстро создавать и закрывать сессии при запросах
engine = create_engine(loader.DATABASE_URL, pool_size=50, max_overflow=100, pool_timeout=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Класс для регистрации моделей и мигрирования
Base = declarative_base()

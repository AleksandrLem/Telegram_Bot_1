import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base

# переменная, в которой функция для получения url базы данных,
# echo=True выводит sql-запросы в терминал
engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

# сессии, чтобы делать запросы в БД, expire_on_commit=False не закрывает сессию
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# создает все таблицы
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# удаляет все таблицы
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

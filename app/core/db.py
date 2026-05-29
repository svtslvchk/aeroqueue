from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. Создаем асинхронный движок (Engine).
# Он управляет пулом соединений с PostgreSQL через драйвер asyncpg.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Включаем логирование SQL-запросов в консоль (очень удобно при разработке)
)

# 2. Создаем фабрику асинхронных сессий.
# expire_on_commit=False критично для асинхронного режима, чтобы объекты не "протухали" после коммита.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 3. Базовый класс для всех будущих SQL-моделей (таблиц).
class Base(DeclarativeBase):
    pass


# 4. Вспомогательная функция (генератор) для эндпоинтов FastAPI.
# Она будет выдавать сессию на каждый HTTP-запрос и гарантированно закрывать её после возврата ответа.
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
import asyncio
import os
from logging.config import fileConfig
from dotenv import load_dotenv  # <-- 1. Добавляем импорт

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

from models import Base
from settings import settings

# 2. Принудительно загружаем переменные из .env до инициализации Alembic
load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    # 3. Гарантируем, что передаем обычную строку, а не SecretStr или None
    # Если в settings используется SecretStr, раскомментируйте строку ниже и закомментируйте текущую:
    # url = settings.DATABASE_URL.get_secret_value() 
    url = str(f"{settings.DATABASE_DRIVER}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DATABASE_URL}/{settings.POSTGRES_DB}")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ... остальной код (do_run_migrations, run_async_migrations, run_migrations_online) без изменений ...



def do_run_migrations(connection):
    """Синхронная функция для выполнения миграций"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode с асинхронным движком."""
    # Переопределяем URL из settings
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = str(f"{settings.DATABASE_DRIVER}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@localhost:5436/{settings.POSTGRES_DB}") # type: ignore
    connectable = async_engine_from_config(
        configuration, # type: ignore
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запускаем асинхронные миграции через asyncio"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

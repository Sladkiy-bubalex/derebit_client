from contextlib import asynccontextmanager
from app.config import create_settings
from app.database.db import create_database_manager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для управления жизненным циклом приложения.
    
    Включает:
    - Инициализацию настроек и менеджера базы данных
    - Очистку ресурсов
    """

    settings = create_settings()
    db_manager = create_database_manager(settings.postgres_url)
    app.state.db_manager = db_manager
    app.state.settings = settings

    yield

    await db_manager.dispose()

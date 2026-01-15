from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager


class DatabaseManager:
    """Асинхронный менеджер базы данных"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    
    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=20,
                max_overflow=10
            )
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Асинхронный контекстный менеджер для сессии"""
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def create_database_manager(database_url: str) -> DatabaseManager:
    return DatabaseManager(database_url)

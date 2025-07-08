import contextlib
from typing import Any, AsyncIterator
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine)

from config import Config

# SQLALCHEMY_DATABASE_URL = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
SQLALCHEMY_DATABASE_URL = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
print(SQLALCHEMY_DATABASE_URL)



Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self,host:str,engine_kwargs: dict[str,Any]={}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._session_factory = async_sessionmaker(expire_on_commit=False,bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise HTTPException(status_code=500, detail="Engine is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._session_factory = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise HTTPException(status_code=500, detail="Session factory is not initialized")
        async with self._engine.connect() as connection:
            try:
                yield connection
            except Exception as e:
                await connection.rollback()
                raise 
    
    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise HTTPException(status_code=500, detail="Session factory is not initialized")
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise
            finally:
                await session.close()

sessionmanger = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL,engine_kwargs={"echo": True})

async def get_db():
    async with sessionmanger.session() as session:
        yield session
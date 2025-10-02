from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.database_url, future=True, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

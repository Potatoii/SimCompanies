import contextlib
import traceback
from asyncio import current_task

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session, async_sessionmaker

import settings
from log_utils import logger


class AsyncDatabase:

    def __init__(self):
        self.MYSQL_HOST = settings.mysql_config["host"]
        self.MYSQL_PORT = settings.mysql_config["port"]
        self.MYSQL_USER = settings.mysql_config["user"]
        self.MYSQL_PASSWORD = settings.mysql_config["password"]
        self.MYSQL_DATABASE = settings.mysql_config["db"]
        self.url = f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def create_async_engine(self):
        engine = create_async_engine(
            self.url
        )
        session = async_scoped_session(
            async_sessionmaker(engine, class_=AsyncSession),
            scopefunc=current_task,
        )
        return session


@contextlib.asynccontextmanager
async def create_session():
    session: AsyncSession = AsyncDatabase().create_async_engine()
    try:
        yield session
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
    except Exception as e:
        logger.error(f"SQL session error: [{traceback.format_exc()}], do rollback!!!")
        raise e
    finally:
        await session.close()


async def search():
    session = create_session()
    result = await session.execute(text("select * from item"))
    print(result.all())


if __name__ == "__main__":
    import asyncio

    asyncio.run(search())

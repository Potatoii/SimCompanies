import functools
from typing import Callable

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from dbengine import create_session


def httpx_client(func: Callable):
    """
    httpx客户端装饰器，需配合关键字参数client使用
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if "client" not in kwargs or not isinstance(kwargs["client"], httpx.AsyncClient):
            async with httpx.AsyncClient() as client:
                kwargs["client"] = client
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper


def transactional(func):
    """
    统一事务装饰器，需配合关键字参数session使用
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if "session" not in kwargs and isinstance(kwargs["session"], AsyncSession):
            async with create_session() as session:
                kwargs["session"] = session
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper

import asyncio
import functools
from typing import Callable


def httpx_client(func: Callable):
    """
    httpx客户端装饰器，需配合关键字参数client使用
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        import httpx
        if "client" not in kwargs or not isinstance(kwargs["client"], httpx.AsyncClient):
            async with httpx.AsyncClient() as client:
                kwargs["client"] = client
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper


def sim_client(func: Callable):
    """
    sim_client装饰器，需配合关键字参数simclient使用
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from sim_request import SimClient
        await asyncio.sleep(0.1)
        if "simclient" not in kwargs or not isinstance(kwargs["simclient"], SimClient):
            async with SimClient() as simclient:
                kwargs["simclient"] = simclient
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper


def retry(max_retries=3, delay=1, notice=False):
    """
    重试装饰器
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        if notice:
                            from notification import notifier
                            await notifier.notify(f"{func.__name__}执行失败, 请检查服务器或账号情况并重启程序: {e}")
                        raise e
                    else:
                        await asyncio.sleep(delay)

        return wrapper

    return decorator

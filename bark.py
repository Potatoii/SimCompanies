import httpx

from decorators import httpx_client
from log_utils import logger


@httpx_client
async def bark_notification(message: str, *, client: httpx.AsyncClient = None):
    """
    bark通知
    """
    url = f"https://api.day.app/q5HsfqJeRjFZsfEuY45KsJ/SimCompanies/{message}"
    try:
        response = await client.get(url)
        if response.status_code == 200:
            response_message = response.json()["message"]
            logger.info(f"bark通知成功: {message}")
        else:
            logger.error(f"bark通知失败: {message}, {response.text}")
    except Exception as e:
        logger.error(f"bark通知失败: {message}, {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(bark_notification("test"))

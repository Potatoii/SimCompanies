import time
from hashlib import md5

import httpx
from httpx import AsyncClient, Cookies

import settings
from decorators import retry
from log_utils import logger


class SimClient:
    def __init__(self):
        self.homepage_url = "https://www.simcompanies.com/zh/"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Host": "www.simcompanies.com",
            "Referer": "https://www.simcompanies.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
            "X-Tz-Offset": "-480"
        }
        self.cookies: Cookies = Cookies()
        self.client: AsyncClient = httpx.AsyncClient(timeout=60)

    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        self.client = None

    async def close(self):
        await self.client.aclose()

    async def generate_cookies(self):
        response = await self.client.get(self.homepage_url)
        cookies = response.cookies
        self.cookies = cookies

    def update_headers(self, url: str):
        timestamp = int(time.time() * 1000)
        api = url.replace("https://www.simcompanies.com", "")
        self.headers.update({
            "X-Prot": md5(f"{api}{timestamp}".encode("utf-8")).hexdigest(),
            "X-Ts": str(timestamp),
        })

    async def request(self, method: str, url: str, body: dict = None):
        self.update_headers(url)
        if not self.cookies:
            await self.generate_cookies()
        self.headers["X-Csrftoken"] = self.cookies.get("csrftoken")
        response = await self.client.request(method, url, json=body, headers=self.headers, cookies=self.cookies)
        return response

    @retry()
    async def get(self, url: str):
        return await self.request("GET", url)

    @retry()
    async def post(self, url: str, body: dict):
        return await self.request("POST", url, body)

    async def login(self):
        auth_api = "https://www.simcompanies.com/api/v2/auth/email/auth/"
        auth_response = await self.post(
            auth_api,
            {
                "email": settings.user_config["email"],
                "password": settings.user_config["password"],
                "timezone_offset": -480,
            }
        )
        if auth_response.status_code != 200:
            logger.error(auth_response.text)
            raise Exception("login failed")
        logger.info("登录成功")
        self.client.cookies = auth_response.cookies

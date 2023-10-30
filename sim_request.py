import json
import time
from hashlib import md5

from httpx import AsyncClient, Cookies

from decorators import httpx_client, retry


class SimClient:
    def __init__(self):
        self.homepage_url = "https://www.simcompanies.com/zh/"
        self.headers = {}
        self.cookies: Cookies = Cookies()

    @httpx_client
    async def generate_cookies(self, *, client: AsyncClient = None):
        response = await client.get(self.homepage_url)
        cookies = response.cookies
        self.cookies = cookies

    async def generate_headers(self, url: str):
        timestamp = int(time.time() * 1000)
        headers = {
            "Accept": "application/json, text/plain, */*", "Content-Type": "application/json;charset=UTF-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Host": "www.simcompanies.com",
            "Referer": "https://www.simcompanies.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
            "X-Prot": md5(f"{url.replace('https://www.simcompanies.com', '')}{timestamp}".encode("utf-8")).hexdigest(),
            "X-Ts": str(timestamp),
            "X-Tz-Offset": "-480"
        }
        self.headers = headers

    @httpx_client
    @retry()
    async def get(self, url: str, *, client: AsyncClient = None):
        await self.generate_headers(url)
        if not self.cookies:
            await self.generate_cookies(client=client)
            self.headers["X-Csrftoken"] = self.cookies.get("csrftoken")
        response = await client.get(url, headers=self.headers, cookies=self.cookies)
        return response

    @httpx_client
    @retry()
    async def post(self, url: str, body: dict, *, client: AsyncClient = None):
        await self.generate_headers(url)
        if not self.cookies:
            await self.generate_cookies(client=client)
            self.headers["X-Csrftoken"] = self.cookies.get("csrftoken")
        self.headers["Content-Length"] = str(len(json.dumps(body)))
        response = await client.post(url, json=body, headers=self.headers, cookies=self.cookies)
        return response

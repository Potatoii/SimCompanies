import time
from httpx import AsyncClient

from decorators import httpx_client


class SimCompanyAuth:
    def __init__(self):
        self.homepage_url = "https://www.simcompanies.com/zh/"
        self.login_api = "https://www.simcompanies.com/api/v2/auth/email/auth/"
        self.me_api = "https://www.simcompanies.com/api/v2/companies/me/"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://www.simcompanies.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
        }

    @httpx_client
    async def get_csrf_token(self, *, client: AsyncClient = None) -> str:
        response = await client.get(self.homepage_url)
        cookie = response.headers.get("set-cookie")
        csrftoken = cookie.split(";")[0].split("=")[1]
        return csrftoken

    @httpx_client
    async def get_cookies(self, email: str, password: str, *, client: AsyncClient = None):
        csrftoken = await self.get_csrf_token()
        milliseconds_since_epoch = int(time.time() * 1000)
        cookies = {
            "csrftoken": csrftoken,
        }
        headers = self.headers.copy()
        headers["X-Csrftoken"] = csrftoken
        headers["X-Ts"] = str(milliseconds_since_epoch)
        headers["X-Tz-Offset"] = "-480"
        response = await client.post(
            self.login_api,
            params={
                "email": email,
                "password": password,
                "timezone_offset": -480,
            },
            headers=self.headers,
            cookies=cookies,
        )
        print(response.cookies)

    @httpx_client
    async def get_my_info(self, *, client: AsyncClient = None):
        response = await client.get(self.me_api)
        print(response.json())


if __name__ == "__main__":
    import asyncio

    sim = SimCompanyAuth()
    # asyncio.run(sim.get_csrf_token())
    asyncio.run(sim.get_cookies("potatoiikiss@qq.com", "Malenia-99"))
    # asyncio.run(sim.get_my_info())

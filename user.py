import settings
from sim_request import SimClient


async def login(client: SimClient) -> SimClient:
    auth_api = "https://www.simcompanies.com/api/v2/auth/email/auth/"
    auth_response = await client.post(
        auth_api,
        {
            "email": settings.user_config["username"],
            "password": settings.user_config["password"],
            "timezone_offset": -480,
        }
    )
    client.cookies = auth_response.cookies
    return client


async def get_user_info():
    """
    Get user info from SimCompanies
    """
    client = SimClient()
    client = await login(client)
    user_api = "https://www.simcompanies.com/api/v2/companies/me/"
    response = await client.get(user_api)
    print(response.json())


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_user_info())

from sim_request import SimClient, login


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

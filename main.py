import asyncio
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient

from dbengine import create_session
from decorators import httpx_client, transactional
from log_utils import logger


def market_url() -> str:
    utc_now = datetime.now(timezone.utc) - timedelta(days=1)
    formatted_datetime = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
    url = f"https://www.simcompanies.com/api/v2/market-ticker/0/{formatted_datetime}/"
    return url


@httpx_client
async def get_encyclopedia_resources(item_id: int | str, *, client: AsyncClient = None) -> dict:
    encyclopedia_url = f"https://www.simcompanies.com/api/v4/zh/0/encyclopedia/resources/1/{item_id}/"
    response = await client.get(encyclopedia_url)
    item_info = response.json()
    # logger.debug(item_info)
    return item_info


@httpx_client
async def main(client: AsyncClient = None):
    response = await client.get(market_url())
    market_list = response.json()
    logger.debug(f"获取到{len(market_list)}条百科数据")
    encyclopedia_future_list = []
    for market_info in market_list:
        encyclopedia_future_list.append(get_encyclopedia_resources(market_info["kind"], client=client))
        # break  # todo
    item_list = await asyncio.gather(*encyclopedia_future_list)
    # logger.debug(item_list)
    for item in item_list:
        async with create_session() as session:
            pass
        sold_at = item["soldAt"]  # 售卖
        sold_at_restaurant = item["soldAtRestaurant"]  # 餐厅售卖
        transportaion = item["transportation"]  # 运输单位(交易所)
        produced_an_hour = item["producedAnHour"]  # 每小时产量
        market_saturation = item["marketSaturation"]  # 市场饱和度
        market_saturation_label = item["marketSaturationLabel"]  # 市场饱和度标签
        needed_for_list = item["neededFor"]  # 用于
        # logger.debug(f"needed_for_list: {needed_for_list}")
        # todo
        produced_from = item["producedFrom"]  # 产自
        # logger.debug(f"produced_from: {produced_from}")
        # todo




if __name__ == "__main__":
    # asyncio.run(get_encyclopedia_resources(125))
    asyncio.run(main())

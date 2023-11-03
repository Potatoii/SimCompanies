import asyncio

from sqlalchemy.orm import Session

import settings
from decorators import sim_client, db_client
from main import get_building_info
from sim_request import SimClient


@sim_client
@db_client
async def auto_production(
        product_id: int,
        quantity: int,
        *,
        simclient: SimClient = None,
        db_session: Session = None
):
    """
    自动生产
    获取该产品的生产建筑, 所需原料
    获取所有建筑信息, 查询是否有空闲的建筑
    获取所有库存信息, 查询是否有足够的原料, 如果有, 则生产; 如果没有, 则自动进货
    :param product_id: 产品id
    :param quantity: 产品数量
    """
    buildings = await get_building_info()
    for building_info in buildings:
        if building_info["id"] in settings.auto_production_config:
            if building_info["status"] == "idle":
                pass
        # resources = await get_resources()
        # for resource in resources:


async def auto_purchase(item_list: list):
    """
    自动进货
    """
    purchase_api = "https://www.simcompanies.com/api/v2/market-order/take/"
    async with SimClient() as client:
        future_list = [client.post(purchase_api, item) for item in item_list]
        [processor_response, electronic_components_response] = await asyncio.gather(*future_list)
        print(processor_response.json(), electronic_components_response.json())


async def auto_selling():
    """
    自动出售
    """
    selling_api = "https://www.simcompanies.com/api/v1/buildings/28032980/busy/"
    pass

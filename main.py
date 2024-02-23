import random
from typing import Dict

from decorators import sim_client
from log_utils import logger
from notification import notifier
from settings import market_config
from sim_request import SimClient
from utils import BuildingInfo, get_building_info
from utils.api_utils import get_market_price, get_my_company


@sim_client
async def building_status_monitor(my_company, simclient: SimClient = None):
    """
    建筑状态监控
    """
    logger.info("开始监控建筑状态")
    idle_building_set = set()
    company_name = my_company.authCompany.company
    while True:
        building_dict: Dict[int, BuildingInfo] = await get_building_info(simclient=simclient)
        for building_id, building_info in building_dict.items():
            building_name = building_info.name
            is_idle = building_id in idle_building_set
            if building_info.status == "idle":
                if not is_idle:
                    logger.info(f"[{company_name}]{building_name}已空闲")
                    await notifier.notify(f"[{company_name}]-{building_name}已空闲")
                    idle_building_set.add(building_id)
            elif is_idle:
                logger.info(f"{building_name}已恢复工作")
                idle_building_set.remove(building_id)
        sleep_time = random.randint(300, 360)
        await asyncio.sleep(sleep_time)


@sim_client
async def price_monitor(my_company, simclient: SimClient = None):
    """
    交易所价格监控
    """
    if market_config.item_list:
        logger.info("开始监控交易行")
        while True:
            for item in market_config.item_list:
                market_item_list = await get_market_price(
                    realm_id=my_company.authCompany.realmId,
                    item_id=item["id"],
                    client=simclient.client
                )
                min_price = -1
                for market_item in market_item_list:
                    if market_item.quality >= item["quality"]:
                        min_price = market_item.price
                if 0 < min_price <= item["price"]:
                    logger.info(f"{item['name']}价格小于等于{item['price']}")
                    await notifier.notify(f"{item['name']}价格小于等于{item['price']}")
            await asyncio.sleep(3600)


@sim_client
async def main(simclient: SimClient = None):
    my_company = await get_my_company(simclient=simclient)
    await asyncio.gather(
        building_status_monitor(my_company, simclient=simclient),
        price_monitor(my_company, simclient=simclient)
    )


if __name__ == "__main__":
    import asyncio
    import sys

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("退出监控")
        sys.exit(0)

import asyncio
import random
from typing import Dict

from log_utils import logger
from notification import notifier
from sim_request import SimClient
from utils import get_building_info, BuildingInfo
from utils.api_utils import get_my_company


async def building_status_monitor():
    """
    建筑状态监控
    """
    idle_building_set = set()
    async with SimClient() as simclient:
        my_company = await get_my_company(simclient=simclient)
        company_name = my_company.authCompany.company
        while True:
            building_dict: Dict[int, BuildingInfo] = await get_building_info(simclient=simclient)
            for building_id, building_info in building_dict.items():
                building_name = building_info.name
                is_idle = building_id in idle_building_set
                if building_info.status == "idle":
                    if not is_idle:
                        logger.info(f"{company_name}-{building_name}已空闲")
                        await notifier.notify(f"{building_name}已空闲")
                        idle_building_set.add(building_id)
                elif is_idle:
                    logger.info(f"{building_name}已恢复工作")
                    idle_building_set.remove(building_id)
            sleep_time = random.randint(300, 360)
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(building_status_monitor())

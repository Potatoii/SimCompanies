import asyncio
import random
from typing import Dict

from decorators import sim_client
from log_utils import logger
from notification import notifier
from schemas.me import MyCompany
from sim_request import SimClient
from utils import BuildingInfo, get_building_info


@sim_client
async def building_status_monitor(my_company: MyCompany, simclient: SimClient = None):
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

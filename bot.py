import asyncio
from typing import Dict

from log_utils import logger
from notification import notifier
from sim_request import SimClient
from utils import get_building_info, BuildingInfo


async def building_status_monitor():
    """
    建筑状态监控
    """
    idle_building_set = set()
    async with SimClient() as simclient:
        while True:
            building_dict: Dict[int, BuildingInfo] = await get_building_info(simclient=simclient)
            for building_id, building_info in building_dict.items():
                building_name = building_info.name
                is_idle = building_id in idle_building_set
                if building_info.status == "idle":
                    if not is_idle:
                        logger.info(f"{building_name}已空闲")
                        await notifier.notify(f"{building_name}已空闲")
                        idle_building_set.add(building_id)
                elif is_idle:
                    logger.info(f"{building_name}已恢复工作")
                    idle_building_set.remove(building_id)
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(building_status_monitor())

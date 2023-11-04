import asyncio

from automation import auto_production
from bark import bark_notification
from sim_request import SimClient
from utils import get_building_info, auto_fetch


async def building_monitor():
    """
    建筑监控
    自动收取建筑物资源
    自动生产
    """
    automatical_factory = {
        "华为研发中心": {"item_id": 20, "quantity": 10},
        "富士康": {"item_id": 47, "quantity": 10},
        # "祖文豪森": {"item_id": 51, "quantity": 10},
        # "魏斯阿赫": {"item_id": 49, "quantity": 10},
    }
    async with SimClient() as simclient:
        while True:
            building_dict = await get_building_info(simclient=simclient)
            for building_name in building_dict:
                building_info = building_dict[building_name]
                if building_info.get("can_fetch"):
                    await auto_fetch(building_info["id"], simclient=simclient)
                if building_info["status"] == "idle":
                    await bark_notification(f"{building_name}已空闲")
                    if building_name in automatical_factory:
                        await auto_production(
                            factory_id=building_info["id"],
                            item_id=automatical_factory[building_name]["item_id"],
                            quantity=automatical_factory[building_name]["quantity"],
                            simclient=simclient
                        )
                        await bark_notification(f"{building_name}已开始工作")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(building_monitor())
import asyncio

from auto_production_test import auto_production_on_board_computer, auto_order, auto_fetch
from bark import bark_notification
from main import get_building_info
from sim_request import SimClient


async def building_monitor():
    """
    建筑监控
    """
    idle_building_list = []
    async with SimClient() as simclient:
        while True:
            building_info_list = await get_building_info(simclient=simclient)
            for building_info in building_info_list:
                if building_info["category"] == "sales" and building_info.get("can_fetch"):
                    await auto_fetch(building_info["id"], simclient=simclient)
                if building_info["status"] == "idle":
                    if building_info["id"] not in idle_building_list:
                        await bark_notification(f"{building_info['name']}已空闲")
                        idle_building_list.append(building_info["id"])
                        if building_info["id"] == 28062782:
                            await auto_order(simclient=simclient)
                            await auto_production_on_board_computer(20, simclient=simclient)
                            await bark_notification(f"{building_info['name']}已开始工作")
                            idle_building_list.remove(building_info["id"])
                else:
                    if building_info["id"] in idle_building_list:
                        await bark_notification(f"{building_info['name']}已开始工作")
                        idle_building_list.remove(building_info["id"])
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(building_monitor())

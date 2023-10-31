import asyncio

from decorators import sim_client
from log_utils import logger
from main import get_building_info, get_resources
from sim_request import SimClient


@sim_client
async def auto_production_on_board_computer(quantity: int, *, simclient: SimClient = None):
    """
    自动生产车载电脑
    """
    factory_id = 28062782
    product_api = f"https://www.simcompanies.com/api/v1/buildings/{factory_id}/busy/"
    body = {
        "kind": 47,  # 产品id
        "amount": quantity,
        "limitQuality": None
    }
    buildings = await get_building_info(simclient=simclient)
    for building_info in buildings:
        if building_info["id"] == factory_id:
            if building_info["status"] == "idle":
                resources = await get_resources(simclient=simclient)
                processor_count = 0
                electronic_components_count = 0
                for resource in resources:
                    resource_id = resource["kind"]["db_letter"]
                    if resource_id == 20:
                        processor_count += resource["amount"]
                    elif resource_id == 21:
                        electronic_components_count += resource["amount"]
                if processor_count < 2 * quantity:
                    processor = {
                        "resource": 20,  # id
                        "quantity": 2 * quantity - processor_count,  # 数量
                        "quality": 0,  # 最低品质
                    }
                    await auto_purchase(processor, simclient=simclient)
                else:
                    logger.info("库存中有足够的处理器")
                if electronic_components_count < 3 * quantity:
                    electronic_components = {
                        "resource": 21,  # id
                        "quantity": 3 * quantity - electronic_components_count,  # 数量
                        "quality": 0,  # 最低品质
                    }
                    await auto_purchase(electronic_components, simclient=simclient)
                else:
                    logger.info("库存中有足够的电子元件")
                response = await simclient.post(product_api, {"kind": 47, "amount": quantity})
                logger.info(response.json()["message"])


@sim_client
async def auto_purchase(item: dict, *, simclient: SimClient = None):
    """
    自动进货
    """
    purchase_url = "https://www.simcompanies.com/api/v2/market-order/take/"
    response = await simclient.post(purchase_url, item)
    logger.info(response.json())


@sim_client
async def auto_order(*, simclient: SimClient = None):
    """
    自动发订单
    """
    resources = await get_resources(simclient=simclient)
    for resource in resources:
        db_letter = resource["kind"]["db_letter"]
        if db_letter == 47:
            on_board_computer_count = resource["amount"]
            resource_id = resource["id"]
            cost = 0
            for c in resource["cost"]:
                cost += resource["cost"][c]
            price = round(cost / on_board_computer_count, 2) + 1
            order_api = "https://www.simcompanies.com/api/v2/market-order/"
            body = {
                "resourceId": resource_id,
                "kind": 47,
                "price": price,
                "quality": 0,
                "quantity": on_board_computer_count,
                "contractTo": "SCANIA Truck"
            }
            response = await simclient.post(order_api, body)
            logger.info(response.json())


if __name__ == "__main__":
    asyncio.run(auto_order())

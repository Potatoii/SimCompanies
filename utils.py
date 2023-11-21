from datetime import datetime

from decorators import sim_client
from sim_request import SimClient

building_chart = {
    "1": "汽车厂",
    "2": "车行",
    "L": "电子产品厂",
}


def date_to_timestamp(date: str) -> int:
    date_object = datetime.fromisoformat(date)
    return int(date_object.timestamp())


def add_resource_info(building_dict: dict, resource_info: dict) -> dict:
    building_dict["status"] = "producing"
    building_dict["resource_amount"] = resource_info["amount"]
    building_dict["resource_item_id"] = resource_info["kind"]
    building_dict["resource_item_name"] = resource_info["name"]
    building_dict["resource_quality"] = resource_info["quality"]
    building_dict["resource_unit_cost"] = round(resource_info["unitCost"], 2)
    return building_dict


def add_sales_info(building_dict: dict, sales_info: dict) -> dict:
    building_dict["status"] = "selling"
    building_dict["selling_amount"] = sales_info["amount"]
    building_dict["selling_price"] = sales_info["price"]
    building_dict["selling_item_id"] = sales_info["kind"]
    building_dict["selling_item_name"] = sales_info["name"]
    building_dict["selling_remaining_profit"] = sales_info["remainingProfit"]
    return building_dict


def add_busy_info(building_dict: dict, business_info: dict) -> dict:
    building_dict["can_fetch"] = business_info.get("canFetch", False)
    business_start = date_to_timestamp(business_info["started"])
    building_dict["business_duration"] = business_info["duration"]
    building_dict["business_start"] = datetime.fromtimestamp(business_start).strftime("%Y-%m-%d %H:%M:%S")
    building_dict["business_end"] = datetime.fromtimestamp(
        business_start + business_info["duration"]
    ).strftime("%Y-%m-%d %H:%M:%S")
    building_dict["business_time_left"] = (
            business_start + business_info["duration"] - int(datetime.now().timestamp())
    )
    building_dict["expanding"] = business_info.get("expanding", False)
    if building_dict["expanding"]:
        building_dict["status"] = "expanding"
    if business_info.get("sales_order"):
        building_dict = add_sales_info(building_dict, business_info["sales_order"])
    if business_info.get("resource"):
        building_dict = add_resource_info(building_dict, business_info["resource"])
    return building_dict


def process_building_info(building_info: dict) -> dict:
    building_dict = {
        "name": building_info["name"],
        "size": building_info["size"],
        "kind": building_chart[building_info["kind"]],
        "category": building_info["category"]
    }
    business_info = building_info.get("busy")
    if business_info:
        building_dict = add_busy_info(building_dict, business_info)
    else:
        building_dict["status"] = "idle"
    return building_dict


@sim_client
async def get_building_info(*, simclient: SimClient = None) -> dict:
    building_api = "https://www.simcompanies.com/api/v2/companies/me/buildings/"
    response = await simclient.get(building_api)
    building_info_list = response.json()
    building_dict = {}
    for building_info in building_info_list:
        building_dict[building_info["id"]] = process_building_info(building_info)
    return building_dict


@sim_client
async def auto_fetch(building_id, *, simclient: SimClient = None):
    """
    自动收钱
    """
    fetch_api = f"https://www.simcompanies.com/api/v2/order/take/{building_id}/"
    response = await simclient.post(fetch_api, {"production": False})
    return response



if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_building_info()))

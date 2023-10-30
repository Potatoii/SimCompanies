from datetime import datetime
from json import JSONDecodeError

from sim_request import SimClient
from user import login

building_chart = {
    "2": "车行",
    "L": "电子产品厂",
}


def date_to_timestamp(date: str) -> int:
    date_object = datetime.fromisoformat(date)
    return int(date_object.timestamp())


async def get_building_info():
    client = SimClient()
    client = await login(client)
    building_api = "https://www.simcompanies.com/api/v2/companies/me/buildings/"
    response = await client.get(building_api)
    try:
        building_info_list = response.json()
    except JSONDecodeError:
        print(response.text)
        return
    buildings = []

    for building_info in building_info_list:
        building_dict = {
            "name": building_info["name"],
            "size": building_info["size"],
            "kind": building_chart[building_info["kind"]],
            "category": building_info["category"]
        }
        business_info = building_info.get("busy")
        if business_info:
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
                building_dict["status"] = "selling"
                selling_info = business_info["sales_order"]
                building_dict["selling_amount"] = selling_info["amount"]
                building_dict["selling_price"] = selling_info["price"]
                building_dict["selling_item_id"] = selling_info["kind"]
                building_dict["selling_item_name"] = selling_info["name"]
                building_dict["selling_remaining_profit"] = selling_info["remainingProfit"]
            if business_info.get("resource"):
                building_dict["status"] = "producing"
                resource_info = business_info["resource"]
                building_dict["resource_amount"] = resource_info["amount"]
                building_dict["resource_item_id"] = resource_info["kind"]
                building_dict["resource_item_name"] = resource_info["name"]
                building_dict["resource_quality"] = resource_info["quality"]
                building_dict["resource_unit_cost"] = round(resource_info["unitCost"], 2)
        else:
            building_dict["status"] = "idle"
        buildings.append(building_dict)
    import json
    return json.dumps(buildings, indent=4, ensure_ascii=False)


# 进货: https://www.simcompanies.com/api/v2/market-order/take/

if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_building_info()))

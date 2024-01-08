from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from decorators import sim_client
from sim_request import SimClient


class ResourceInfo(BaseModel):
    amount: int
    kind: int
    name: str
    quality: int
    unit_cost: float


class SalesInfo(BaseModel):
    amount: int
    price: float
    kind: int
    name: str
    remaining_profit: float


class BusinessInfo(BaseModel):
    can_fetch: bool = False
    duration: float
    start: str
    end: str
    time_left: int = None
    expanding: bool = False
    sales_order: Optional[SalesInfo] = None
    resource: Optional[ResourceInfo] = None


class BuildingInfo(BaseModel):
    id: int
    name: str
    size: int
    kind: str
    category: str
    status: str
    busy: BusinessInfo = None


def date_to_timestamp(date: str) -> int:
    date_object = datetime.fromisoformat(date)
    return int(date_object.timestamp())


def add_resource_info(building_dict: dict, resource: dict) -> dict:
    building_dict["status"] = "producing"
    building_dict["resource"] = ResourceInfo(
        amount=resource.get("amount"),
        kind=resource.get("kind"),
        name=resource.get("name"),
        quality=resource.get("quality"),
        unit_cost=resource.get("unitCost"),
    )
    return building_dict


def add_sales_info(building_dict: dict, sales_order: dict) -> dict:
    building_dict["status"] = "selling"
    building_dict["sales_order"] = SalesInfo(
        amount=sales_order.get("amount"),
        price=sales_order.get("price"),
        kind=sales_order.get("kind"),
        name=sales_order.get("name"),
        remaining_profit=sales_order.get("remainingProfit"),
    )
    return building_dict


def add_busy_info(building_dict: dict, business_info: dict) -> dict:
    business_start = date_to_timestamp(business_info["started"])
    business_end = business_start + business_info["duration"]
    sales_order = business_info.get("sales_order")
    if sales_order:
        building_dict = add_sales_info(building_dict, sales_order)
        business_info.pop("sales_order")
    resource = business_info.get("resource")
    if resource:
        building_dict = add_resource_info(building_dict, resource)
        business_info.pop("resource")
    building_dict["busy"] = BusinessInfo(
        start=datetime.fromtimestamp(business_start).strftime("%Y-%m-%d %H:%M:%S"),
        end=datetime.fromtimestamp(business_end).strftime("%Y-%m-%d %H:%M:%S"),
        time_left=business_end - int(datetime.now().timestamp()),
        sales_order=building_dict.get("sales_order"),
        resource=building_dict.get("resource"),
        **business_info,
    )
    return building_dict


def process_building_info(building_info: dict) -> BuildingInfo:
    building_dict = building_info.copy()
    building_dict["status"] = "idle"
    if building_info.get("busy"):
        building_dict = add_busy_info(building_dict, building_info["busy"])
        building_dict["status"] = "busy"
    return BuildingInfo(**building_dict)


@sim_client
async def get_building_info(*, simclient: SimClient = None) -> dict:
    building_api = "https://www.simcompanies.com/api/v2/companies/me/buildings/"
    response = await simclient.get(building_api)
    building_info_list = response.json()
    building_dict = {}
    for building_info in building_info_list:
        building_dict[building_info["id"]] = process_building_info(building_info)
    return building_dict


if __name__ == "__main__":
    import asyncio
    import json
    from typing import Dict

    buildings: Dict[int, BuildingInfo] = asyncio.run(get_building_info())
    for building_id, building in buildings.items():
        print(
            json.dumps(
                building.model_dump(),
                ensure_ascii=False,
                indent=2
            )
        )

import asyncio
from typing import List

from pydantic import BaseModel

from decorators import sim_client
from sim_request import SimClient
from utils.api_utils import get_item_info


class SimpleResource(BaseModel):
    name: str
    db_letter: int


class SimpleProducedFrom(BaseModel):
    resource: SimpleResource
    amount: float


class SimpleItem(BaseModel):
    name: str
    db_letter: int
    producedAt: str
    producedFrom: List[SimpleProducedFrom]
    producedAnHour: float


@sim_client
async def populate_produced_from(
        realm_id: int,
        economy_state: int,
        item: SimpleItem,
        item_dict: dict,
        *,
        simclient: SimClient = None
):
    stack = [item]
    while stack:
        current_item = stack.pop()
        for produced_from in current_item.producedFrom:
            produced_from_resource_db_letter: int = produced_from.resource.db_letter
            if produced_from_resource_db_letter in item_dict:
                produced_from.resource = item_dict[produced_from_resource_db_letter]
            else:
                await asyncio.sleep(0.5)
                sub_item = await get_item_info(
                    realm_id,
                    economy_state,
                    produced_from_resource_db_letter,
                    simclient=simclient
                )
                sub_item = SimpleItem(**sub_item.model_dump())
                for sub_producedFrom in sub_item.producedFrom:
                    sub_producedFrom.resource = SimpleResource(**sub_producedFrom.resource.model_dump())
                item_dict[produced_from_resource_db_letter] = sub_item.model_dump()
                stack.append(sub_item)


def dict_to_nested_dict(nested_dict: dict, flat_dict: dict):
    for sub_item in nested_dict.get("producedFrom", []):
        sub_item_id = sub_item["resource"]["db_letter"]
        if sub_item_id in flat_dict:
            sub_item["resource"] = flat_dict[sub_item_id]
            dict_to_nested_dict(sub_item["resource"], flat_dict)


def calculate_produced_time(nested_dict: dict, total_produced_from: dict, amount: float = 1):
    """
    计算上游产品生产时间
    """
    if nested_dict["db_letter"] not in total_produced_from:
        total_produced_from[nested_dict["db_letter"]] = {
            "name": nested_dict["name"],
            "producedAnHour": nested_dict["producedAnHour"],
            "amount": amount
        }
    else:
        total_produced_from[nested_dict["db_letter"]]["amount"] += amount
    sub_list = nested_dict["producedFrom"]
    for sub in sub_list:
        sub_item = sub["resource"]
        calculate_produced_time(sub_item, total_produced_from, sub["amount"])


@sim_client
async def production_calculator(
        realm_id: int,
        economy_state: int,
        item_id: int,
        *,
        simclient: SimClient = None
) -> dict:
    """
    生产计算器
    :return: 生产关系
    {
        "95": {
            "name": "喷气客机",
            "producedAnHour": 0.069656026702761734,
            "amount": 1
        },
        "77": {
            "name": "机身",
            "producedAnHour": 3.5592458078660107,
            "amount": 40.0
        }
    }
    """
    item_info = await get_item_info(realm_id, economy_state, item_id, simclient=simclient)
    item_info = SimpleItem(**item_info.model_dump())
    item_dict = {item_id: item_info.model_dump()}
    await populate_produced_from(realm_id, economy_state, item_info, item_dict, simclient=simclient)
    nested_dict = item_dict[item_id]
    dict_to_nested_dict(nested_dict, item_dict)
    total_produced_from = {}
    calculate_produced_time(nested_dict, total_produced_from)
    return total_produced_from


if __name__ == "__main__":
    print(asyncio.run(production_calculator(0, 0, 95)))

import math
from typing import List

from decorators import sim_client
from schemas import Executive
from schemas.retail import RetailModel
from sim_request import SimClient
from utils.api_utils import get_retail_model, get_executives, executive_filter, get_my_company, get_user_company, \
    get_item_info


class RetailInfo:
    """
    销售情况
    """

    def __init__(
            self,
            realm_id: int,
            economy_state: int,
            item_id: int,
    ):
        """
        :param realm_id: 领域(商业大亨|企业家)
        :param economy_state: 经济状态(0:景气|1:平缓|2:萧条)
        :param item_id: 物品id
        """
        self.realm_id = realm_id
        self.economy_state = economy_state
        self.item_id = item_id

    @staticmethod
    def merge_sales_modifier(sales_modifier: int, executives: List[Executive], recreation_bonus: int) -> int:
        """
        合并销售加成
        :param sales_modifier: 销售速度加成
        :param executives: 高管
        :param recreation_bonus: 娱乐加速(城堡|公园|人工湖)
        :return: 销售速度加成
        """
        executives = executives if executives else []
        cmo_skills = 0
        for executive in executives:
            if executive.position == "cmo":
                cmo_skills += executive.skills["cmo"]
            elif executive.position[0] == "c":
                cmo_skills += executive.skills["cmo"] / 4
        cmo_skills = math.floor(cmo_skills)
        return (sales_modifier or 0) + math.floor(cmo_skills / 3) + recreation_bonus

    @staticmethod
    def calculate(
            retail_model: RetailModel,
            sales_modifier: int,
            price: float,
            quality: int,
            market_saturation: float,
            acceleration: int,
            building_size: int,
    ) -> float:
        """
        计算销售速度
        """
        p = (math.pow(price * retail_model.xMultiplier + (
                retail_model.xOffsetBase + (
                max(market_saturation - 0.3 if market_saturation < 0.3 else market_saturation - quality * 0.24,
                    0.1 - 0.24 * 2) - 0.5) / retail_model.marketSaturationDiv),
                      retail_model.power) * retail_model.yMultiplier + retail_model.yOffset) * 100 / acceleration / building_size
        return 100 * 3600 / (p - p * sales_modifier / 100)

    @sim_client
    async def calculate_retail_per_hour(
            self,
            price: float,
            quality: int,
            building_size: int,
            *,
            simclient: SimClient = None
    ) -> float:
        """
        计算每小时销售量
        :param price: 售价
        :param quality: 品质
        :param building_size: 建筑等级
        :param simclient: SimClient
        :return: 每小时销售量
        """
        retail_model = await get_retail_model(self.realm_id, self.economy_state, self.item_id, simclient=simclient)
        executives = await get_executives(simclient=simclient)
        executives = executive_filter(executives)
        my_company = await get_my_company(simclient=simclient)
        acceleration = my_company.levelInfo.acceleration.multiplier
        user_info = await get_user_company(my_company.authCompany.company, realm_id=self.realm_id, simclient=simclient)
        recreation_bonus = user_info.company.recreationBonus
        sales_modifier = self.merge_sales_modifier(my_company.authCompany.salesModifier, executives, recreation_bonus)
        item = await get_item_info(self.realm_id, self.economy_state, self.item_id)
        market_saturation = item.marketSaturation
        return self.calculate(
            retail_model,
            sales_modifier,
            price,
            quality,
            market_saturation,
            acceleration,
            building_size
        )


if __name__ == "__main__":
    import asyncio

    retail_info = RetailInfo(0, 1, 56)
    print(asyncio.run(retail_info.calculate_retail_per_hour(5449.38, 2, 2)))

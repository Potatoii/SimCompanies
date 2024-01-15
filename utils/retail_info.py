import math
from typing import List, Optional

from decorators import sim_client
from schemas.encyclopedia import EncyclopediaItem
from schemas.executive import Executive
from schemas.resouces import Resource
from schemas.user import User
from sim_request import SimClient
from utils.api_utils import get_retail_model, get_executives, executive_filter, get_my_company, get_user_company, \
    get_item_info, get_resource


class RetailInfo:
    """
    销售情况
    """

    def __init__(
            self,
            realm_id: int,
            economy_state: int,
            item_id: int,
            retail_model=None,
            acceleration=None,
            sales_modifier=None,
            market_saturation=None
    ):
        """
        :param realm_id: 领域(0:商业大亨|1:企业家)
        :param economy_state: 经济状态(0:萧条|1:平缓|2:景气)
        :param item_id: 物品id
        """
        self.realm_id = realm_id
        self.economy_state = economy_state
        self.item_id = item_id
        self.retail_model = retail_model
        self.acceleration = acceleration
        self.sales_modifier = sales_modifier
        self.market_saturation = market_saturation
        self.user_info: Optional[User] = None
        self.executives: Optional[List[Executive]] = None
        self.item: Optional[EncyclopediaItem] = None

    @sim_client
    async def setup(self, *, simclient: SimClient = None):
        self.retail_model = await get_retail_model(self.realm_id, self.economy_state, self.item_id, simclient=simclient)
        executives = await get_executives(simclient=simclient)
        self.executives = executive_filter(executives)
        my_company = await get_my_company(simclient=simclient)
        self.acceleration = my_company.levelInfo.acceleration.multiplier
        user_info: User = await get_user_company(my_company.authCompany.company, self.realm_id, simclient=simclient)
        self.user_info = user_info
        recreation_bonus = user_info.company.recreationBonus
        self.sales_modifier = self.merge_sales_modifier(my_company.authCompany.salesModifier, self.executives,
                                                        recreation_bonus)
        item = await get_item_info(self.realm_id, self.economy_state, self.item_id, simclient=simclient)
        self.market_saturation = item.marketSaturation
        self.item = item

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
    def merge_admin_modifier(administration_overhead: float, executives: List[Executive]) -> float:
        """
        合并管理费用修正
        :param administration_overhead: 管理费用修正
        :param executives: 高管
        :return: 管理费用修正
        """
        executives = executives if executives else []
        coo_skills = 0
        for executive in executives:
            if executive.position == "coo":
                coo_skills += executive.skills["coo"]
            elif executive.position[0] == "c":
                coo_skills += executive.skills["coo"] / 4
        coo_skills = math.floor(coo_skills)
        return administration_overhead + coo_skills / 100 - administration_overhead * coo_skills / 100

    def units_an_hour(
            self,
            pricing: float,
            quality: int,
            building_size: int,
    ) -> float:
        """
        销售速度计算器
        :param pricing: 定价
        :param quality: 品质
        :param building_size: 建筑等级
        :return: 每小时销售量
        """
        p = (math.pow(
            pricing * self.retail_model.xMultiplier + (
                    self.retail_model.xOffsetBase + (
                    max(
                        self.market_saturation - 0.3 if self.market_saturation < 0.3 else self.market_saturation - quality * 0.24,
                        0.1 - 0.24 * 2
                    ) - 0.5
            ) / self.retail_model.marketSaturationDiv
            ),
            self.retail_model.power
        ) * self.retail_model.yMultiplier + self.retail_model.yOffset) * 100 / self.acceleration / building_size
        return 100 * 3600 / (p - p * self.sales_modifier / 100)

    def pricing_calculator(
            self,
            retail_time: float,
            building_size: int,
            quantity: int,
            quality: int,
    ) -> float:
        """
        定价计算器(固定时间)
        """
        try:
            pricing = (math.pow(
                (100 * 3600 * retail_time * self.acceleration * building_size / quantity / (
                        100 - self.sales_modifier) - self.retail_model.yOffset) / self.retail_model.yMultiplier,
                1 / self.retail_model.power
            ) - self.retail_model.xOffsetBase - (max(
                self.market_saturation - 0.3 if self.market_saturation < 0.3 else self.market_saturation - quality * 0.24,
                0.1 - 0.24 * 2
            ) - 0.5) / self.retail_model.marketSaturationDiv) / self.retail_model.xMultiplier
        except ValueError:
            pricing = 0
        return pricing

    @sim_client
    async def profit_calculator(
            self,
            pricing: float,
            resource_name: str,
            building_size: int,
            quantity: int,
            quality: int,
            resource: Resource = None,
            *,
            simclient: SimClient = None
    ) -> float:
        """
        利润计算器
        """
        if not resource:
            resource = await get_resource(resource_name, quality, simclient=simclient)
        total_cost = sum(getattr(resource.cost, attr) for attr in resource.cost.__annotations__)
        unit_cost = total_cost / resource.amount
        administration_overhead = self.user_info.company.administrationOverhead
        admin_modifier = self.merge_admin_modifier(administration_overhead, self.executives)
        wages = self.item.storeBaseSalary * building_size * admin_modifier
        retail_speed = self.units_an_hour(pricing, quality, building_size)
        retail_time = quantity / retail_speed
        profit = (pricing - unit_cost) * quantity - wages * retail_time
        return profit


if __name__ == "__main__":
    import asyncio

    retail_info = RetailInfo(0, 0, 56)
    asyncio.run(retail_info.setup())
    # print(retail_info.units_an_hour(5000, 2, 2))
    # print(retail_info.pricing_calculator(24, 2, 1000, 2))
    print(asyncio.run(retail_info.profit_calculator(
        5110,
        "豪华燃油车",
        3,
        45,
        2
    )))

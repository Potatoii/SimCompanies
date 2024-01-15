import ast
from datetime import datetime, timedelta
import re
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from decorators import sim_client, httpx_client
from schemas.encyclopedia import EncyclopediaItem
from schemas.executive import Executive
from schemas.market import MarketItem
from schemas.me import MyCompany
from schemas.resouces import Resource
from schemas.retail import RetailModel
from schemas.user import User
from sim_request import SimClient


@sim_client
async def get_retail_model(
        realm_id: int,
        economy_state: int,
        item_id: int,
        *,
        simclient: SimClient = None
) -> RetailModel:
    """
    获取零售模型
    :param realm_id: 领域(0:商业大亨|1:企业家)
    :param economy_state: 经济状态(0:萧条|1:平缓|2:景气)
    :param item_id: 物品id
    :param simclient: SimClient
    :return: 零售模型
    """
    resource_url = f"https://www.simcompanies.com/zh/encyclopedia/{realm_id}/resource/{item_id}/"
    response = await simclient.raw_get(resource_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    # 获取js
    script_tags = soup.find_all("script", {"type": "module"})
    js_url = script_tags[0].attrs.get("src")
    js = await simclient.raw_get(js_url)
    # 正则匹配取出retail_model
    pattern = re.compile(r"\{(\d+):{(\d+):(.*?)}}}}")
    match = pattern.search(js.text)
    retail_model = match.group(0)
    retail_model = re.sub(r"(\w+):", r"'\1':", retail_model)
    retail_model = ast.literal_eval(retail_model)
    retail_model = retail_model[str(realm_id)][str(economy_state)][str(item_id)]
    retail_model = RetailModel(**retail_model)
    return retail_model


@sim_client
async def get_executives(*, simclient: SimClient = None) -> List[Executive]:
    """
    获取高管信息
    :param simclient: SimClient
    :return: 高管列表
    """
    executives_url = "https://www.simcompanies.com/api/v2/companies/me/executives/"
    response = await simclient.get(executives_url)
    executives = response.json()
    executives = [Executive(**executive) for executive in executives]
    return executives


def executive_filter(executives: List[Executive]) -> List[Executive]:
    """
    员工筛选
    :param executives: 高管列表
    :return: 高管列表
    """
    now_timestamp = datetime.now().timestamp() * 1000
    filtered_executives = []
    for executive in executives:
        if executive.position[0] != "c":
            continue
        if now_timestamp - int(datetime.timestamp(datetime.fromisoformat(executive.start)) * 1000) < 10800000:
            continue
        if executive.positionAccelerated:
            continue
        if executive.isCandidate:
            continue
        if executive.currentTraining:
            if not executive.currentTraining.accelerated:
                continue
            if int(datetime.timestamp(
                    datetime.fromisoformat(executive.currentTraining.datetime))) > now_timestamp - 97200000:
                continue
        if executive.strikeUntil:
            if int(datetime.timestamp(datetime.fromisoformat(executive.strikeUntil))) > now_timestamp:
                continue
        filtered_executives.append(executive)
    return filtered_executives


@sim_client
async def get_my_company(*, simclient: SimClient = None) -> MyCompany:
    """
    获取自己的公司信息
    :param simclient: SimClient
    :return: 自己的公司信息
    """
    url = "https://www.simcompanies.com/api/v2/companies/me/"
    response = await simclient.get(url)
    company = response.json()
    company = MyCompany(**company)
    return company


@sim_client
async def get_user_company(user_name: str, realm_id: int = 0, *, simclient: SimClient = None) -> User:
    """
    获取指定公司信息
    :param user_name: 公司名
    :param realm_id: 领域(0:商业大亨|1:企业家)
    :param simclient: SimClient
    :return: 公司信息
    """
    url = f"https://www.simcompanies.com/api/v2/companies-by-company/{realm_id}/{user_name}/"
    response = await simclient.get(url)
    user = response.json()
    user = User(**user)
    return user


@sim_client
async def get_item_info(
        realm_id: int,
        economy_state: int,
        item_id: int,
        *,
        simclient: SimClient = None
) -> Optional[EncyclopediaItem]:
    """
    获取物品信息
    :param realm_id: 领域(0:商业大亨|1:企业家)
    :param economy_state: 经济状态(0:萧条|1:平缓|2:景气)
    :param item_id: 物品id
    :param simclient: SimClient
    :return: 物品信息
    """
    wiki_url = f"https://www.simcompanies.com/api/v4/zh/{realm_id}/encyclopedia/resources/{economy_state}/{item_id}/"
    response = await simclient.raw_get(wiki_url)
    if response.status_code == 404:
        return None
    item_info = response.json()
    item_info["soldAtRestaurant"] = True if item_info.get("soldAtRestaurant") else False
    item = EncyclopediaItem(**item_info)
    return item


@httpx_client
async def get_market_overview(realm_id: int, *, client: httpx.AsyncClient = None) -> List:
    """
    获取交易行价格概览
    :param realm_id: 领域(0:商业大亨|1:企业家)
    :param client: httpx.AsyncClient
    :return: 交易行价格概览
    """
    previous_day = datetime.utcnow() - timedelta(days=1)
    iso_format_str = previous_day.isoformat()
    iso_format_str = iso_format_str[:-3] + "Z"
    market_url = f"https://www.simcompanies.com/api/v2/market-ticker/{realm_id}/{iso_format_str}/"
    response = await client.get(market_url)
    market_info = response.json()
    return market_info


@httpx_client
async def get_market_price(realm_id: int, item_id: int, *, client: httpx.AsyncClient = None) -> List[MarketItem]:
    """
    获取交易行价格
    :param realm_id: 领域(0:商业大亨|1:企业家)
    :param item_id: 物品id
    :param client: httpx.AsyncClient
    :return: 交易行价格
    """
    item_url = f"https://www.simcompanies.com/api/v3/market/{realm_id}/{item_id}/"
    response = await client.get(item_url)
    item_list = response.json()
    item_list = [MarketItem(**item) for item in item_list]
    return item_list


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_item_info(0, 0, 91)))
    # print(asyncio.run(get_my_company()))

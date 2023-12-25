import ast
from datetime import datetime
import re
from typing import List

from bs4 import BeautifulSoup

from decorators import sim_client
from schemas import Executive
from schemas.item import Item
from schemas.me import Company
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
    :param realm_id: 领域(商业大亨|企业家)
    :param economy_state: 经济状态(0:景气|1:平缓|2:萧条)
    :param item_id: 物品id
    :param simclient: SimClient
    :return: 零售模型
    """
    resource_url = f"https://www.simcompanies.com/zh/encyclopedia/{realm_id}/resource/{item_id}/"
    response = await simclient.client.get(resource_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    # 获取js
    script_tags = soup.find_all("script", {"type": "module"})
    js_url = script_tags[0].attrs.get("src")
    js = await simclient.client.get(js_url)
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
        if (
                executive.position[0] != "c"
                or now_timestamp - datetime.timestamp(datetime.fromisoformat(executive.start)) * 1000 >= 10800000
                or executive.positionAccelerated
                or executive.isCandidate
                or not executive.currentTraining
                or executive.currentTraining.accelerated
                or datetime.timestamp(
            datetime.fromisoformat(executive.currentTraining.datetime)) <= now_timestamp - 97200000
                or not executive.strikeUntil
                or datetime.timestamp(datetime.fromisoformat(executive.strikeUntil)) <= now_timestamp
        ):
            filtered_executives.append(executive)
    return filtered_executives


@sim_client
async def get_my_company(*, simclient: SimClient = None) -> Company:
    """
    获取自己的公司信息
    :param simclient: SimClient
    :return: 自己的公司信息
    """
    url = "https://www.simcompanies.com/api/v2/companies/me/"
    response = await simclient.get(url)
    company = response.json()
    company = Company(**company)
    return company


@sim_client
async def get_user_company(user_name: str, realm_id: int = 1, *, simclient: SimClient = None) -> User:
    """
    获取指定公司信息
    :param user_name: 公司名
    :param realm_id: 领域(商业大亨|企业家)
    :param simclient: SimClient
    :return: 公司信息
    """
    url = f"https://www.simcompanies.com/api/v2/companies-by-company/{realm_id}/{user_name}/"
    response = await simclient.get(url)
    user = response.json()
    user = User(**user)
    return user


@sim_client
async def get_item_info(realm_id: int, economy_state: int, item_id: int, *, simclient: SimClient = None) -> Item:
    """
    获取物品信息
    :param realm_id: 领域(商业大亨|企业家)
    :param economy_state: 经济状态(0|1:平缓|2)
    :param item_id: 物品id
    :param simclient: SimClient
    :return: 物品信息
    """
    wiki_url = f"https://www.simcompanies.com/api/v4/zh/{realm_id}/encyclopedia/resources/{economy_state}/{item_id}/"
    response = await simclient.get(wiki_url)
    item_info = response.json()
    item = Item(**item_info)
    return item


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_my_company()))

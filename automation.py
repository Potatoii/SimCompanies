import asyncio

from sqlalchemy.orm import Session

from bark import bark_notification
from database.models import Item
from decorators import sim_client, db_client
from log_utils import logger
from main import get_resources
from sim_request import SimClient


@sim_client
@db_client
async def auto_production(
        factory_id: int,
        item_id: int,
        quantity: int,
        *,
        simclient: SimClient = None,
        db_session: Session = None
):
    """
    自动生产
    获取该产品所需原料
    获取所有库存信息, 查询是否有足够的原料, 如果有, 则生产; 如果没有, 则自动进货
    :param factory_id: 工厂id
    :param item_id: 产品id
    :param quantity: 产品数量
    :param simclient: http会话
    :param db_session: 数据库会话
    """
    item = db_session.query(Item).filter(Item.item_id == item_id).first()  # noqa
    resources = await get_resources(simclient=simclient)
    resource_dict = {resource["kind"]["db_letter"]: resource["amount"] for resource in resources}
    for produced_from in item.produced_from:
        if produced_from.produced_from_id in resource_dict and produced_from.amount * quantity <= resource_dict[
            produced_from.produced_from_id]:
            logger.info("库存中有足够的原料")
        else:
            components = {
                "resource": produced_from.produced_from_id,  # id
                "quantity": produced_from.amount * quantity - resource_dict.get(produced_from.produced_from_id, 0),
                "quality": 0,  # 最低品质
            }
            await auto_purchase(components, simclient=simclient)
    product_api = f"https://www.simcompanies.com/api/v1/buildings/{factory_id}/busy/"
    response = await simclient.post(product_api, {"kind": item_id, "amount": quantity})
    if response.status_code == 200:
        logger.info(response.json()["message"])
    else:
        logger.error(response.json()["message"])
        await bark_notification(response.json()["message"])


@sim_client
async def auto_purchase(item: dict, *, simclient: SimClient = None):
    """
    自动进货
    """
    purchase_url = "https://www.simcompanies.com/api/v2/market-order/take/"
    response = await simclient.post(purchase_url, item)
    if response.status_code == 200:
        logger.info(response.json()["message"])
    else:
        logger.error(response.json()["message"])
        await bark_notification(response.json()["message"])
    return response


async def auto_selling():
    """
    自动出售
    """
    selling_api = "https://www.simcompanies.com/api/v1/buildings/28032980/busy/"
    pass


if __name__ == "__main__":
    asyncio.run(auto_production(28208660, 20, 10))

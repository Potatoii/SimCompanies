import asyncio
import os.path
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

import settings
from database.models import create_table, Item, ItemProducedFrom, ItemNeededFor
from decorators import httpx_client, db_client
from log_utils import logger


def market_url() -> str:
    utc_now = datetime.now(timezone.utc) - timedelta(days=1)
    formatted_datetime = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
    url = f"https://www.simcompanies.com/api/v2/market-ticker/0/{formatted_datetime}/"
    return url


@httpx_client
async def get_encyclopedia_resources(item_id: int | str, *, client: AsyncClient = None) -> dict:
    encyclopedia_url = f"https://www.simcompanies.com/api/v4/zh/0/encyclopedia/resources/1/{item_id}/"
    response = await client.get(encyclopedia_url)
    item_info = response.json()
    return item_info


@httpx_client
@db_client
async def update_items(*, client: AsyncClient = None, db_session: Session = None):
    logger.info("开始获取产品数据")
    response = await client.get(market_url())
    market_list = response.json()
    logger.info(f"获取到{len(market_list)}条产品数据")
    encyclopedia_future_list = []
    for market_info in market_list:
        encyclopedia_future_list.append(get_encyclopedia_resources(market_info["kind"], client=client))
    item_list = await asyncio.gather(*encyclopedia_future_list)
    for item in item_list:
        new_item = Item(
            item_id=item["db_letter"],
            name=item["name"],
            transportation=item["transportation"],
            sold_at=item["soldAt"],
            sold_at_restaurant=item["soldAtRestaurant"],
            produced_an_hour=item["producedAnHour"],
            market_saturation=item["marketSaturation"],
            market_saturation_label=item["marketSaturationLabel"]
        )
        try:
            existing_item = db_session.query(Item).filter(
                Item.item_id == new_item.item_id  # noqa
            ).one()
            existing_item = new_item
        except NoResultFound:
            db_session.add(new_item)
        for produced_from in item["producedFrom"]:
            new_item_produced_from = ItemProducedFrom(
                item_id=item["db_letter"],
                produced_from_id=produced_from["resource"]["db_letter"],
                amount=produced_from["amount"]
            )
            try:
                existing_item_produced_from = db_session.query(ItemProducedFrom).filter(
                    ItemProducedFrom.item_id == new_item_produced_from.item_id,  # noqa
                    ItemProducedFrom.produced_from_id == new_item_produced_from.produced_from_id  # noqa
                ).one()
                existing_item_produced_from = new_item_produced_from
            except NoResultFound:
                db_session.add(new_item_produced_from)
        for needed_for in item["neededFor"]:
            new_needed_for = ItemNeededFor(
                item_id=item["db_letter"],
                needed_for_id=needed_for["db_letter"],
            )
            try:
                existing_needed_for = db_session.query(ItemNeededFor).filter(
                    ItemNeededFor.item_id == new_needed_for.item_id,  # noqa
                    ItemNeededFor.needed_for_id == new_needed_for.needed_for_id  # noqa
                ).one()
                existing_needed_for = new_needed_for
            except NoResultFound:
                db_session.add(new_needed_for)
    db_session.commit()
    logger.info("更新产品数据完成")


@db_client
async def main(*, db_session: Session = None):
    if not os.path.exists(f"{settings.root_path}/database/SimCompanies.db"):
        logger.info("数据库不存在, 正在初始化数据库")
        tables = create_table(db_session=db_session)
        logger.info(f"当前数据库中的表: {tables}")
        logger.info("--------------------")

        await init_items(db_session=db_session)


if __name__ == "__main__":
    asyncio.run(init_items())

import datetime

from sqlalchemy import Column, Integer, DateTime, func, String, Float
from sqlalchemy.orm import declarative_base, MappedColumn, relationship, backref, Session
from sqlalchemy.sql import schema

from decorators import db_client

Base = declarative_base()


class PriorityColumn(MappedColumn):
    def __init__(self, *args, sort_order=-1, **kwargs):
        super().__init__(*args, sort_order=sort_order, **kwargs)


class ModelBase(Base):
    __abstract__ = True

    id = PriorityColumn(Integer, primary_key=True, autoincrement=True)
    created_time = PriorityColumn(DateTime, default=datetime.datetime.now)
    updated_time = PriorityColumn(DateTime, onupdate=datetime.datetime.now)


class Ix:
    def __new__(cls, table_name, *keys, unique: bool = False, **kwargs):
        name = cls._get_ix_prefix(table_name, *keys, unique=unique)
        if unique:
            return schema.UniqueConstraint(*keys, name=name)
        else:
            return schema.Index(name, *keys, **kwargs)

    @classmethod
    def _get_ix_prefix(cls, table_name, *keys, unique: bool = False):
        pattern = {
            True: "uix_" + table_name + "_" + "_".join(keys).lower(),
            False: "ix_" + table_name + "_" + "_".join(keys).lower(),
        }
        return pattern.get(unique is True)


class Item(ModelBase):
    """
    产品表
    """
    __tablename__ = "item"
    item_id = Column(Integer, nullable=False, comment="产品id")
    name = Column(String(32), nullable=False, comment="产品名称")
    transportation = Column(Float(8), comment="运输单位(交易所)")
    sold_at = Column(String(32), comment="零售单位")
    sold_at_restaurant = Column(String(32), comment="是否在餐厅销售")
    produced_an_hour = Column(Float(16), comment="每小时产量")
    market_saturation = Column(Float(16), comment="市场饱和度")
    market_saturation_label = Column(String(8), comment="市场饱和度标签")

    produced_from = relationship(
        "ItemProducedFrom",
        primaryjoin="foreign(ItemProducedFrom.item_id) == Item.item_id",
        lazy="selectin",
        backref=backref(
            "item",
            lazy="joined"
        )
    )

    needed_for = relationship(
        "ItemNeededFor",
        primaryjoin="foreign(ItemNeededFor.item_id) == Item.item_id",
        lazy="selectin",
        backref=backref(
            "item",
            lazy="joined"
        )
    )

    __table_args__ = (
        Ix(__tablename__, "item_id", unique=True),
        Ix(__tablename__, "name"),
    )


class ItemProducedFrom(ModelBase):
    """
    产品产自表
    """
    __tablename__ = "item_produced_from"
    item_id = Column(Integer, nullable=False, comment="产品id")
    produced_from_id = Column(Integer, nullable=False, comment="产自产品id")
    amount = Column(Float(8), nullable=False, comment="数量")

    __table_args__ = (
        Ix(__tablename__, "item_id", "produced_from_id", unique=True),
    )


class ItemNeededFor(ModelBase):
    """
    产品用于表
    """
    __tablename__ = "item_needed_for"
    item_id = Column(Integer, nullable=False, comment="产品id")
    needed_for_id = Column(Integer, nullable=False, comment="用于产品id")

    __table_args__ = (
        Ix(__tablename__, "item_id", "needed_for_id", unique=True),
    )


@db_client
def create_table(*, db_session: Session = None) -> list:
    from sqlalchemy import text
    from database import engine
    Base.metadata.create_all(engine)
    result = db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = [row[0] for row in result]
    return tables


if __name__ == "__main__":
    print(create_table())

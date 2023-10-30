from sqlalchemy import Column, Integer, DateTime, func, text, SMALLINT, String, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy.sql import schema

import settings

Base = declarative_base()


class DatabaseConfig(object):
    def __init__(self):
        self.MYSQL_HOST = settings.mysql_config["host"]
        self.MYSQL_PORT = settings.mysql_config["port"]
        self.MYSQL_USER = settings.mysql_config["user"]
        self.MYSQL_PASSWORD = settings.mysql_config["password"]
        self.MYSQL_DATABASE = settings.mysql_config["db"]

    def sync_mysql_connection(self):
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}/{self.MYSQL_DATABASE}"

    def async_mysql_connection(self):
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}/{self.MYSQL_DATABASE}"


class TBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_id = Column(Integer)
    created_time = Column(DateTime, server_default=func.now())
    updated_id = Column(Integer)
    updated_time = Column(DateTime)
    deleted = Column(SMALLINT, server_default=text("0"))


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


class Item(TBase):
    """
    产品表
    """
    __tablename__ = "item"
    item_id = Column(Integer, nullable=False, comment="产品id")
    name = Column(String(24), nullable=False, comment="产品名称")
    transportation = Column(Float(8), comment="运输单位(交易所)")
    sold_at = Column(String(24), comment="零售单位")
    sold_at_restaurant = Column(Boolean, comment="是否在餐厅销售")
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
        Ix(__tablename__, "item_id"),
        Ix(__tablename__, "name"),
    )


class ItemProducedFrom(TBase):
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


class ItemNeededFor(TBase):
    """
    产品用于表
    """
    __tablename__ = "item_needed_for"
    item_id = Column(Integer, nullable=False, comment="产品id")
    needed_for_id = Column(Integer, nullable=False, comment="用于产品id")

    __table_args__ = (
        Ix(__tablename__, "item_id", "needed_for_id", unique=True),
    )


if __name__ == "__main__":
    from sqlalchemy import create_engine

    cfg = DatabaseConfig()
    sync_engine = create_engine(
        cfg.sync_mysql_connection()
    )
    Base.metadata.create_all(sync_engine)

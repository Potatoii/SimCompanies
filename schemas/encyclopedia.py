from typing import List, Optional

from pydantic import BaseModel


class Resource(BaseModel):
    name: str
    image: str
    db_letter: int
    transportation: float
    retailable: bool
    research: bool
    exchangeTradable: bool
    realmAvailable: bool


class ProducedFrom(BaseModel):
    resource: Resource
    amount: float


class NeededFor(BaseModel):
    name: str
    image: str
    db_letter: int
    transportation: float
    retailable: bool
    research: bool
    exchangeTradable: bool
    realmAvailable: bool


class RetailData(BaseModel):
    averagePrice: float
    amountSoldRestaurant: int
    demand: float
    date: str
    label: str


class ImprovesQualityOf(BaseModel):
    name: str
    image: str
    db_letter: int
    transportation: float
    retailable: bool
    research: bool
    exchangeTradable: bool
    realmAvailable: bool


class EncyclopediaItem(BaseModel):
    name: str
    image: str
    db_letter: int
    transportation: float
    retailable: bool
    research: bool
    exchangeTradable: bool
    realmAvailable: bool
    producedFrom: List[ProducedFrom]
    soldAt: Optional[str]
    soldAtRestaurant: Optional[str]
    producedAt: str
    neededFor: List[NeededFor]
    transportNeeded: float
    producedAnHour: float
    baseSalary: float
    averageRetailPrice: Optional[float]
    marketSaturation: Optional[float]
    marketSaturationLabel: Optional[str]
    storeBaseSalary: Optional[float]
    retailData: List[RetailData]
    improvesQualityOf: List[ImprovesQualityOf]

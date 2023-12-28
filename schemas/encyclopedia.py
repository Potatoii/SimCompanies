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
    amount: int


class RetailData(BaseModel):
    averagePrice: float
    amountSoldRestaurant: int
    demand: float
    date: str
    label: str


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
    soldAt: str
    soldAtRestaurant: Optional[str]
    producedAt: str
    neededFor: List
    transportNeeded: float
    producedAnHour: float
    baseSalary: float
    averageRetailPrice: float
    marketSaturation: float
    marketSaturationLabel: str
    storeBaseSalary: float
    retailData: List[RetailData]
    improvesQualityOf: List

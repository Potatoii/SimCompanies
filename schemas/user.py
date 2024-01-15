from typing import Optional, List, Any
from pydantic import BaseModel, Field


class Building(BaseModel):
    id: int
    kind: str
    position: str
    image: str
    category: str
    name: str
    cost: int


class History(BaseModel):
    value: int
    buildingValue: int
    patentsValue: int


class Company(BaseModel):
    id: int
    company: str
    realmId: int
    moderatorSign: bool
    logo: str
    level: int
    levelName: str
    hqImage: str
    note: str
    maxBuildings: int
    rank: int
    rating: str
    dateJoined: str
    dateReset: Optional[str] = Field(None, description="上次重置时间(字段已废弃)")
    lastSeen: str
    previousNames: List[str]
    workers: int
    administrationOverhead: float
    productionModifier: int
    salesModifier: int
    recreationBonus: int
    history: History
    bondsSold: Optional[Any]
    bondsSoldInterest: Optional[Any]
    ratingBracket: str
    courseId: Optional[Any]
    countryCodeIsoUserSet: str


class Player(BaseModel):
    communicationRestricted: bool
    timezoneOffset: int


class User(BaseModel):
    player: Player
    company: Company
    online: str
    buildings: List[Building]
    certificates: List
    bonds: Optional[Any]
    displayCase: List
    upInRank: str
    downInRank: str
    collectibles: List
    supporter: bool

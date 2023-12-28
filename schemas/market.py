from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Seller(BaseModel):
    id: int
    company: str
    realmId: int
    logo: Optional[str]
    certificates: int
    contest_wins: int
    npc: bool
    courseId: Optional[int]
    ip: str


class MarketItem(BaseModel):
    id: int
    kind: int
    quantity: int
    quality: int
    price: float
    seller: Seller
    posted: datetime
    fees: int

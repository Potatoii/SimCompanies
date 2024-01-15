from typing import List

from pydantic import BaseModel


class Kind(BaseModel):
    name: str
    image: str
    db_letter: int
    transportation: float
    retailable: bool
    research: bool
    exchangeTradable: bool


class Cost(BaseModel):
    workers: float
    admin: float
    material1: float
    material2: float
    material3: float
    material4: float
    material5: float
    market: float


class Resource(BaseModel):
    id: int
    amount: int
    quality: int
    kind: Kind
    blocked: bool
    cost: Cost
    materials: List[str]

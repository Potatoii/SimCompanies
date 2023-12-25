from pydantic import BaseModel


class RetailModel(BaseModel):
    fnc: str
    xMultiplier: float
    yMultiplier: float
    yOffset: float
    xOffsetBase: float
    marketSaturationDiv: float
    power: int

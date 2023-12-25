from typing import Optional, Dict, Any
from pydantic import BaseModel


class Employer(BaseModel):
    id: int
    company: str
    logo: str
    realmId: int


class CurrentTraining(BaseModel):
    id: int
    datetime: str
    type: str
    description: str
    covered: bool
    employer: Employer
    accelerated: bool


class Executive(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    genome: str
    currentEmployer: int
    isCandidate: bool
    created: str
    accelerated: bool
    salary: int
    strikeUntil: Optional[Any]  # 没碰到过罢工不知道长啥样
    skills: Dict[str, int]
    position: str
    start: str
    positionAccelerated: bool
    currentTraining: Optional[CurrentTraining]

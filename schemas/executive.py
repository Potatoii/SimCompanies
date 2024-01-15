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
    name: str = None
    age: int = None
    gender: str = None
    genome: str = None
    currentEmployer: int = None
    isCandidate: bool = None
    created: str
    accelerated: bool = None
    salary: int = None
    strikeUntil: Optional[Any] = None  # 没碰到过罢工不知道长啥样
    skills: Dict[str, int] = None
    position: str
    start: str
    positionAccelerated: bool = None
    currentTraining: Optional[CurrentTraining] = None

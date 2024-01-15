from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Capabilities(BaseModel):
    research: bool
    scrape: bool
    bonds: bool
    governmentOrders: bool
    executives: bool
    hqUpdates: bool


class Acceleration(BaseModel):
    multiplier: int = Field(description="加速倍数")
    until: Optional[Any]


class LevelInfo(BaseModel):
    ratingCode: str
    levelName: str
    level: int
    inTutorial: bool
    acceleration: Acceleration
    experience: int
    experienceToNextLevel: int
    maxBuildings: int
    capabilities: Capabilities
    timeLimit: int


class AuthUser(BaseModel):
    playerId: int
    isModerator: bool
    auditAccess: bool
    newspaperEditor: bool
    isAdmin: bool
    aiSuggestions: bool
    supporterPurchased: bool
    supporter: bool
    countryCodeIso: str
    email: str
    bouncingEmail: bool
    language: str
    age18: bool
    communicationRestricted: bool
    featureFlags: str


class AuthCompany(BaseModel):
    companyId: int
    company: str = Field(description="公司名")
    moderatorSign: bool
    hqImage: str
    money: int
    exchangedToday: int
    simBoosts: int
    popupNotifications: Dict[str, bool]
    productionModifier: int
    salesModifier: int
    countryCodeIsoUserSet: str
    rank: Optional[int]
    extraExecutiveSlots: int
    extraBuildingSlots: int
    displayCaseSlots: int
    logo: str
    startingPackPurchased: bool
    maxTags: int
    courseId: Optional[Any]
    showOnlineIndicator: bool
    testCategory: int
    level: int
    realmId: int


class Temporals(BaseModel):
    sale: str
    contest: Dict[Any, Any]
    economyState: int


class Preferences(BaseModel):
    theme: str


class MyCompany(BaseModel):
    authCompany: AuthCompany
    authUser: AuthUser
    levelInfo: LevelInfo
    temporals: Temporals
    preferences: Preferences
    encKey: Optional[Any]
    courses: list

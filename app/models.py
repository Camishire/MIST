from pydantic import BaseModel
from typing import Optional

class CreateEventRequest(BaseModel):
    """Old simple request (backwards compatibility)"""
    title: str
    ips: list[str]
    distribution: int = 2
    threat_level_id: int = 2
    analysis: int = 1
    creator_key: str


class AttributeModel(BaseModel):
    """Single attribute"""
    category: str
    type: str
    value: str
    comment: Optional[str] = ""
    to_ids: Optional[bool] = False


class CreateEventFullRequest(BaseModel):
    """Full event creation request"""
    creator_key: str
    date: str
    distribution: int
    threat_level_id: int
    analysis: int
    info: str
    tags: list[str] = []
    galaxies: list[str] = []
    attributes: list[AttributeModel] = []
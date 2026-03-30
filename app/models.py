from pydantic import BaseModel, Field
from typing import List, Optional

class CreateEventRequest(BaseModel):
    title: str = Field(..., description="Event pavadinimas")
    ips: List[str] = Field(default=[], description="IP adresų sąrašas")
    auto_enrich: bool = Field(default=True, description="Automatiškai enrichinti?")

class AddAttributeRequest(BaseModel):
    type: str = Field(..., description="Attribute tipas (ip-src, ip-dst, domain, hash, etc)")
    value: str = Field(..., description="Attribute reikšmė")
    auto_comment: bool = Field(default=True, description="Automatiškai pridėti komentarą?")

class AddTagsRequest(BaseModel):
    categories: List[str] = Field(default=["geo", "sector"], description="Tag kategorijos")

class EventResponse(BaseModel):
    event_id: str
    info: str
    status: str
    message: str
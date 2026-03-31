from pydantic import BaseModel

class CreateEventRequest(BaseModel):
    title: str
    ips: list
    distribution: int = 2          # Optional su default
    threat_level_id: int = 2       # Optional su default
    analysis: int = 1              # Optional su default
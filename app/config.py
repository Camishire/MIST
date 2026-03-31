from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    misp_url: str
    misp_api_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # ← Pridėk šią eilutę!

settings = Settings()
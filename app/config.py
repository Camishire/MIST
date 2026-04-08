from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    misp_url: str
    misp_api_key: str
    api_key_name: str = "X-API-Key"
    api_key_value: str = "mist-secret-key-2026"
    abuseipdb_api_key: Optional[str] = None
    opencti_url: str
    opencti_api_key: str
    misp_aurelija_api_key: Optional[str] = None
    misp_viktorija_api_key: Optional[str] = None
    misp_kamile_api_key: Optional[str] = None
    misp_evija_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

settings = Settings()
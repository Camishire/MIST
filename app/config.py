from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # MISP
    misp_url: str
    misp_api_key: str
    
    # OpenCTI
    opencti_url: str
    opencti_api_key: str
    
    # Elasticsearch
    elastic_url: str
    elastic_api_key: str
    
    # Wazuh (optional)
    wazuh_url: Optional[str] = None
    wazuh_username: Optional[str] = None
    wazuh_password: Optional[str] = None
    
    # AbuseIPDB (optional)
    abuseipdb_api_key: Optional[str] = None
    
    # API Security
    api_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
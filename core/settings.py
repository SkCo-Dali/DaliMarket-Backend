# core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    COSMOS_URI: str
    COSMOS_KEY: str
    COSMOS_DATABASE: str
    COSMOS_OPPORTUNITY_LEADS_CONTAINER: str
    COSMOS_OPPORTUNITY_LEADS_PARTITION_KEY: str
    COSMOS_OPPORTUNITY_DETAIL_CONTAINER: str
    COSMOS_OPPORTUNITY_DETAIL_PARTITION_KEY: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

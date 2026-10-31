import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_provider: str = "gemini"
    llm_model_name: str = "gemini-1.5-flash"
    gemini_api_key: str = ""
    local_api_base: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

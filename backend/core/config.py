import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8080
    frontend_port: int = 8501
    backend_url: str = "http://127.0.0.1:8080"
    allowed_origins: str = "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173"

    # AI Configuration
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    gemini_api_key: str = ""
    llm_model_name: str = "gemini-3.1-flash-lite"
    vision_model_name: str = "gemini-3.1-flash-lite"
    embedding_model_name: str = "text-embedding-004"
    image_model_name: str = "imagen-3.0-generate-002"
    ollama_base_url: str = "http://localhost:11434"

    # Database
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "friday_db"
    mysql_user: str = "root"
    mysql_password: str = ""

    # Storage paths
    vector_store_dir: str = str(BASE_DIR / "data" / "chroma")
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    generated_dir: str = str(BASE_DIR / "data" / "generated")
    max_upload_size_mb: int = 1024  # 1 GB upload limit

    # Desktop & Integrations
    desktop_control_enabled: bool = True
    allow_dangerous_operations: bool = False
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:8888/callback"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def effective_api_key(self) -> str:
        """Returns LLM API key with fallback to GEMINI_API_KEY or OS environment variables."""
        return self.llm_api_key or self.gemini_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

    @property
    def parsed_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def mysql_url(self) -> str:
        from urllib.parse import quote_plus
        pwd = quote_plus(self.mysql_password) if self.mysql_password else ""
        user = quote_plus(self.mysql_user)
        return f"mysql+pymysql://{user}:{pwd}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"

settings = Settings()

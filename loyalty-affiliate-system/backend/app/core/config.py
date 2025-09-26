from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, computed_field, model_validator


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database Settings
    DATABASE_URL: str = "mssql+pyodbc://username:password@localhost/loyalty_db?driver=ODBC+Driver+17+for+SQL+Server"

    # WhatsApp Settings
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v17.0"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "your-whatsapp-verify-token"

    # Redis Settings (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379"

    # Email Settings (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Logic ERP Settings
    LOGIC_ERP_DATABASE_URL: str = ""
    LOGIC_ERP_API_KEY: str = ""

    @model_validator(mode='after')
    def assemble_cors_origins(self) -> 'Settings':
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            self.BACKEND_CORS_ORIGINS = [
                i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",")
            ]
        return self

    @model_validator(mode='after')
    def assemble_server_host(self) -> 'Settings':
        if isinstance(self.SERVER_HOST, str):
            self.SERVER_HOST = AnyHttpUrl(self.SERVER_HOST)
        return self

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
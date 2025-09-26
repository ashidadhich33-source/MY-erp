from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, computed_field, model_validator, Field
import secrets


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database Settings
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # WhatsApp Settings
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v17.0"
    WHATSAPP_ACCESS_TOKEN: str = Field(default="", description="WhatsApp API access token")
    WHATSAPP_VERIFY_TOKEN: str = Field(default_factory=lambda: secrets.token_hex(32))

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
    LOGIC_ERP_DATABASE_URL: str = Field(default="", description="Logic ERP database URL")
    LOGIC_ERP_API_KEY: str = Field(default="", description="Logic ERP API key")

    # ERP Connection Settings (for MSSQL direct access)
    ERP_HOST: str = Field(default="", description="ERP database host")
    ERP_PORT: int = Field(default=1433, description="ERP database port")
    ERP_DATABASE: str = Field(default="", description="ERP database name")
    ERP_USERNAME: str = Field(default="", description="ERP database username")
    ERP_PASSWORD: str = Field(default="", description="ERP database password")
    ERP_DRIVER: str = Field(default="ODBC Driver 17 for SQL Server", description="ODBC driver name")

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

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()
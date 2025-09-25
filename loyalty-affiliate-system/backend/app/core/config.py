import os
from typing import List


class Settings:
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
    ]

    # Database
    DATABASE_URL: str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=loyalty_system;UID=sa;PWD=your_password"

    # WhatsApp
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""

    APP_NAME: str = "Loyalty & Affiliate Management System"
    DEBUG: bool = True

    @classmethod
    def from_env(cls):
        """Load settings from environment variables"""
        settings = cls()

        # Load from .env file if it exists
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if hasattr(settings, key):
                            setattr(settings, key, value)

        # Override with environment variables
        for key in ['SECRET_KEY', 'DATABASE_URL', 'WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_VERIFY_TOKEN']:
            env_value = os.getenv(key)
            if env_value:
                setattr(settings, key, env_value)

        return settings


settings = Settings.from_env()
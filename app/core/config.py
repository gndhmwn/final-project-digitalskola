# app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Variabel aplikasi
    database_url: str
    secret_key: str
    bride_name: str
    groom_name: str
    default_security_code: Optional[str] = None
    
    # Variabel database baru yang ditambahkan untuk Docker Compose
    mysql_root_password: str
    mysql_database: str
    mysql_user: str
    mysql_password: str

    class Config:
        env_file = ".env"

settings = Settings()
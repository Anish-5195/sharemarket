from typing import ClassVar
from pydantic_settings import BaseSettings,SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str 
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 

    KITE_API_KEY: ClassVar[str] 
    KITE_API_SECRET: ClassVar[str] 
    REFRESH_SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int  

    BACKEND_URL: str  # (e.g="http://localhost:8000")

    SMTP_SERVER: str      # e.g. "smtp.gmail.com"
    SMTP_PORT: int        # e.g. 587
    EMAIL_SENDER: str    # e.g. "myemail@gmail.com"
    EMAIL_PASSWORD: str    # your email password or app password
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()





import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Project"

    class Config:
        env_file = ".env"

settings = Settings()
"""
Application configuration loaded from environment variables.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_mode: str = "demo"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # In Docker: __file__ = /app/app/backend/app/core/config.py → parent x3 = /app/app/backend
    database_url: str = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'parkshare.db'}"
    
    # Scoring weights
    weight_density: float = 0.25
    weight_collective_housing: float = 0.25
    weight_parking_pressure: float = 0.30
    weight_motorization: float = 0.20
    
    # LLM (optional)
    llm_api_key: str = ""
    llm_api_url: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_mode: str = "demo"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    database_url: str = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'parkshare.db'}"

    weight_density: float = 0.25
    weight_collective_housing: float = 0.25
    weight_parking_pressure: float = 0.30
    weight_motorization: float = 0.20

    llm_api_key: str = ""
    llm_api_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

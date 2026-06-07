# config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    storage_account_name: str
    storage_account_container_name: str = "architecture-documents"
    cosmos_db_url: str
    cosmos_db_account_name: str = "ArchitectureAdvisor"
    cosmos_db_key: str
    servicebus_namespace: str

    class Config:
        env_file = ".env"


settings = Settings()

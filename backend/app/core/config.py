import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://helm:helm@localhost:5432/northbound_helm",
    )


settings = Settings()


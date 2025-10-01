from pydantic import BaseModel
from dotenv import load_dotenv
import os

class Settings(BaseModel):
    app_env: str = "development"
    db_url: str = "sqlite:///./ai_trader.sqlite"
    data_cache_ttl: int = 60

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            db_url=os.getenv("DB_URL", "sqlite:///./ai_trader.sqlite"),
            data_cache_ttl=int(os.getenv("DATA_CACHE_TTL", "60")),
        )

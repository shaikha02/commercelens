from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Application settings resolved independently of the current working directory."""

    model_config = ConfigDict(frozen=True)

    app_name: str = "CommerceLens Phase-1 Backend"
    api_prefix: str = "/api/v1"
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/app.db"
    static_dir: str = "../frontend/dist"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    app_base_url: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sqlite_path(self) -> Path | None:
        if self.database_url.startswith("sqlite:///"):
            rel = self.database_url.replace("sqlite:///", "", 1)
            return Path(__file__).resolve().parent.parent / rel
        return None


settings = Settings()

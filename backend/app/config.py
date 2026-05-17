import os
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _platform_public_url() -> str | None:
    render = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if render:
        return render.rstrip("/")
    railway = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway:
        return f"https://{railway}".rstrip("/")
    fly = os.getenv("FLY_APP_NAME", "").strip()
    if fly:
        return f"https://{fly}.fly.dev".rstrip("/")
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/app.db"
    static_dir: str = "../frontend/dist"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    app_base_url: str = "http://localhost:5173"

    @model_validator(mode="after")
    def apply_platform_defaults(self) -> "Settings":
        public = _platform_public_url()
        if not public:
            return self
        if self.app_base_url in ("http://localhost:5173", "http://127.0.0.1:5173"):
            self.app_base_url = public
        origins = {o.strip() for o in self.cors_origins.split(",") if o.strip()}
        origins.add(public)
        self.cors_origins = ",".join(sorted(origins))
        return self

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

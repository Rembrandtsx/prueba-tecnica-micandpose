"""Configuration settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── Database ─────────────────────────────────────
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "task_management"
    db_user: str = "root"
    db_password: str = "changeme"

    # ─── App ──────────────────────────────────────────
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000

    # ─── Computed ─────────────────────────────────────
    @property
    def database_url(self) -> str:
        """Generate MySQL connection URL for asyncmy."""
        return (
            f"mysql+asyncmy://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

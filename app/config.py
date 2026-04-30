from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UIT Petcare"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    secret_key: str = "replace-with-a-long-random-string"

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "mysql"
    db_password: str = "123456"
    db_name: str = "petcare"

    sql_dump_path: str = "../petcare_php/petcare_database.sql"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def resolved_dump_path(self) -> Path:
        path = Path(self.sql_dump_path)
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()


settings = Settings()

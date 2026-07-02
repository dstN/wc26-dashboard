from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_host: str = "db"
    mysql_port: int = 3306
    mysql_user: str = "wc26user"
    mysql_password: str = "wc26pass"
    mysql_database: str = "wc26"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    contact_to_email: str = "dustin.tramm@yinside.de"
    allowed_origin: str = "http://localhost:5173"

    ingest_secret_key: str = ""
    pdf_watch_dir: str = "./pdfs"
    ingestion_python: str = "python3"
    ingestion_module_dir: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def async_db_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )

    @property
    def sync_db_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )


settings = Settings()

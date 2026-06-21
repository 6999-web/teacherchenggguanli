from typing import List, Optional
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "教研室工作考评系统"
    API_V1_STR: str = "/api"

    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "jysuser"
    MYSQL_PASSWORD: str = "change_me"
    MYSQL_DB: str = "jys_data"
    MYSQL_PORT: int = 3306
    DATABASE_URL: Optional[str] = None

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "change_me"
    MINIO_SECRET_KEY: str = "change_me"
    MINIO_BUCKET: str = "teaching-office-attachments"
    MINIO_SECURE: bool = False

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5001",
        "http://localhost:5002",
        "http://localhost:3817",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002",
        "http://127.0.0.1:3817",
        "http://101.33.211.98",
        "http://101.33.211.98:80",
        "http://101.33.211.98:3000",
        "http://101.33.211.98:5173",
        "http://101.33.211.98:8000",
        "https://101.33.211.98",
        "https://101.33.211.98:443",
        "http://101.33.210.169:38888",
        "http://101.33.210.169",
        "http://101.33.210.169:80",
        "https://101.33.210.169",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def model_post_init(self, __context) -> None:
        if not self.DATABASE_URL:
            password = quote_plus(self.MYSQL_PASSWORD)
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQL_USER}:{password}"
                f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
            )


settings = Settings()

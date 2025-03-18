from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis


class Settings(BaseSettings):
    DEBUG: bool = True
    DB_NAME: str = Field("postgres")
    DB_HOST: str = Field("localhost")
    DB_PORT: str = Field("5432")
    DB_USER: str = Field("postgres")
    DB_PASS: str = Field("postgres")

    redis: Redis | None = Field(default=None, init=False)
    REDIS_HOST: str = Field("localhost")
    REDIS_PORT: str = Field("6379")

    SESSION_COOKIE_NAME: str = Field("kleofas_session")
    BASE_URL: str
    FLOWER_URL: str = "http://localhost:5555"
    SESSION_SECRET: str

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = ""
    AWS_S3_ENDPOINT_URL: str = ""
    AWS_S3_USE_SSL: bool = False
    AWS_DEFAULT_ACL: str = ""
    AWS_QUERYSTRING_AUTH: bool = False
    AWS_S3_CUSTOM_DOMAIN: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""

    model_config = SettingsConfigDict(env_file="conf/.env", env_file_encoding="utf-8")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = Redis(
            host=self.REDIS_HOST, port=self.REDIS_PORT, decode_responses=True
        )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

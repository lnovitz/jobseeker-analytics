import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from typing import List
from typing_extensions import Annotated
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    GOOGLE_SCOPES: Annotated[List[str], NoDecode]
    REDIRECT_URI: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_API_KEY: str
    COOKIE_SECRET: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int
    CLIENT_SECRETS_FILE: str = "credentials.json"
    ENV: str = "dev"

    @field_validator("GOOGLE_SCOPES", mode="before")
    @classmethod
    def decode_scopes(cls, v: str) -> List[str]:
        logger.info("Decoding scopes from string: %s", v)
        return json.loads(v.strip("'\""))

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

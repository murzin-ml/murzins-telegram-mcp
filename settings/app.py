from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.constants import ENV_FILES, LogLevel


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding="utf-8", extra="ignore")

    LOG_LEVEL: LogLevel = LogLevel.WARNING

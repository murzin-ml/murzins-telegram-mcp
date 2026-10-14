from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.constants import DEFAULT_DEVICE_MODEL, DEFAULT_QUIET_PERIOD_SEC, DEFAULT_REPLY_TIMEOUT_SEC, ENV_FILES


def _split_refs(raw: str) -> frozenset[str]:
    return frozenset(item.strip().lstrip("@").lower() for item in raw.split(",") if item.strip())


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding="utf-8", extra="ignore")

    # Ключи приложения с https://my.telegram.org/apps
    TG_API_ID: int = 0
    TG_API_HASH: SecretStr = SecretStr("")
    # Строку сессии записывает `make login`
    TG_SESSION: SecretStr = SecretStr("")
    TG_DEVICE_MODEL: str = DEFAULT_DEVICE_MODEL

    # Юзернеймы ботов через запятую; пусто — любой бот, но только бот
    TG_ALLOWED_BOTS: str = ""
    # Чтение и поиск по чатам; выключено по умолчанию
    TG_READ_ENABLED: bool = False
    # Чаты, закрытые для чтения: id из tg_chats или @username через запятую
    TG_READ_DENIED_CHATS: str = ""

    TG_REPLY_TIMEOUT_SEC: float = DEFAULT_REPLY_TIMEOUT_SEC
    TG_QUIET_PERIOD_SEC: float = DEFAULT_QUIET_PERIOD_SEC

    @property
    def allowed_bots(self) -> frozenset[str]:
        return _split_refs(self.TG_ALLOWED_BOTS)

    @property
    def denied_chats(self) -> frozenset[str]:
        return _split_refs(self.TG_READ_DENIED_CHATS)

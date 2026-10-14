import pytest

from settings.app import AppSettings
from settings.telegram import TelegramSettings

_LEAKABLE_ENV_VARS = (
    "LOG_LEVEL",
    "TG_API_ID",
    "TG_API_HASH",
    "TG_SESSION",
    "TG_DEVICE_MODEL",
    "TG_ALLOWED_BOTS",
    "TG_READ_ENABLED",
    "TG_READ_DENIED_CHATS",
    "TG_REPLY_TIMEOUT_SEC",
    "TG_QUIET_PERIOD_SEC",
)


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Тесты не должны видеть ни переменные окружения, ни настоящий .env.local с сессией
    for name in _LEAKABLE_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setitem(TelegramSettings.model_config, "env_file", None)
    monkeypatch.setitem(AppSettings.model_config, "env_file", None)

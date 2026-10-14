from enum import StrEnum
from pathlib import Path
from typing import Final


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
# Секреты живут только в .env.local: он не попадает в git (см. белый список .gitignore).
SECRETS_FILE: Final[Path] = PROJECT_ROOT / ".env.local"
ENV_FILES: Final[tuple[Path, Path]] = (PROJECT_ROOT / ".env", SECRETS_FILE)

APP_VERSION: Final[str] = "0.1.1"
DEFAULT_DEVICE_MODEL: Final[str] = "murzins-telegram-mcp"
DEFAULT_REPLY_TIMEOUT_SEC: Final[float] = 45.0
DEFAULT_QUIET_PERIOD_SEC: Final[float] = 4.0

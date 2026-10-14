from dataclasses import dataclass
from pathlib import Path

from telethon import utils

from app.core.diagnostics.dto import DiagnosticsReportDTO
from app.infra.adapters.telegram import TelegramClientProvider
from app.infra.exceptions import MurzinsTelegramInfraException
from settings.telegram import TelegramSettings


@dataclass(slots=True, frozen=True)
class DiagnosticsService:
    """
    Проверка окружения без вывода секретов: только «задано / не задано» и имя аккаунта.
    """

    settings: TelegramSettings
    client_provider: TelegramClientProvider
    secrets_file: Path

    async def check(self) -> DiagnosticsReportDTO:
        session_valid = False
        account: str | None = None
        error: str | None = None
        try:
            client = await self.client_provider.get()
            me = await client.get_me()
            session_valid = True
            account = utils.get_display_name(me) + (f" (@{me.username})" if me.username else "")
        except MurzinsTelegramInfraException as exc:
            error = str(exc)
        except OSError as exc:
            error = f"нет связи с Telegram: {exc}"

        return DiagnosticsReportDTO(
            secrets_file_exists=self.secrets_file.is_file(),
            api_keys_set=bool(self.settings.TG_API_ID and self.settings.TG_API_HASH.get_secret_value()),
            session_set=bool(self.settings.TG_SESSION.get_secret_value()),
            session_valid=session_valid,
            account=account,
            read_enabled=self.settings.TG_READ_ENABLED,
            allowed_bots=tuple(sorted(self.settings.allowed_bots)),
            denied_chats_count=len(self.settings.denied_chats),
            error=error,
        )

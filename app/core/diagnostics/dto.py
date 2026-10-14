from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DiagnosticsReportDTO:
    secrets_file_exists: bool
    api_keys_set: bool
    session_set: bool
    session_valid: bool
    account: str | None
    read_enabled: bool
    allowed_bots: tuple[str, ...]
    denied_chats_count: int
    error: str | None = None

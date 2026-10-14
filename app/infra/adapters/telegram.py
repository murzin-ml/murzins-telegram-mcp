import asyncio
from dataclasses import dataclass, field
from typing import Any

from telethon import TelegramClient, utils
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError
from telethon.sessions import StringSession
from telethon.tl import types

from app.core.chats.constants import ButtonKind, ChatKind
from app.core.chats.dto import ButtonDTO, ChatDTO, FileDTO, MessageDTO
from app.infra.exceptions import TelegramConfigError, TelegramSessionError
from settings.constants import APP_VERSION
from settings.telegram import TelegramSettings

# Ошибки Telethon, которыми он сообщает о несуществующем чате или юзернейме
ENTITY_NOT_FOUND_ERRORS: tuple[type[Exception], ...] = (ValueError, UsernameNotOccupiedError, UsernameInvalidError)


def build_client(*, settings: TelegramSettings, session: str) -> TelegramClient:
    """
    Создаёт клиент Telethon. Пустая сессия нужна только для входа.

    :param settings: Настройки Telegram.
    :param session: Строка сессии.
    :return: Неподключённый клиент.
    """
    api_hash = settings.TG_API_HASH.get_secret_value()
    missing = [name for name, value in (("TG_API_ID", settings.TG_API_ID), ("TG_API_HASH", api_hash)) if not value]
    if missing:
        raise TelegramConfigError(missing=", ".join(missing))
    return TelegramClient(
        StringSession(session),
        settings.TG_API_ID,
        api_hash,
        device_model=settings.TG_DEVICE_MODEL,
        app_version=APP_VERSION,
    )


@dataclass(slots=True)
class TelegramClientProvider:
    """
    Один подключённый клиент на процесс. Подключение ленивое: сервер стартует
    и отдаёт список инструментов даже без сессии, а ошибка всплывает при вызове.
    """

    settings: TelegramSettings
    _client: TelegramClient | None = field(default=None, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def get(self) -> TelegramClient:
        async with self._lock:
            if self._client is None:
                session = self.settings.TG_SESSION.get_secret_value()
                if not session:
                    raise TelegramSessionError()
                client = build_client(settings=self.settings, session=session)
                await client.connect()
                if not await client.is_user_authorized():
                    await client.disconnect()
                    raise TelegramSessionError()
                self._client = client
            return self._client


def chat_kind(entity: Any) -> ChatKind:
    if isinstance(entity, types.User):
        return ChatKind.BOT if entity.bot else ChatKind.USER
    if isinstance(entity, types.Channel):
        return ChatKind.GROUP if entity.megagroup else ChatKind.CHANNEL
    return ChatKind.GROUP


def to_chat_dto(entity: Any, *, unread: int | None = None, last_message_date: Any = None) -> ChatDTO:
    return ChatDTO(
        id=utils.get_peer_id(entity),
        title=utils.get_display_name(entity) or "",
        kind=chat_kind(entity),
        username=getattr(entity, "username", None),
        unread=unread,
        last_message_date=last_message_date,
    )


def to_button_dto(button: Any) -> ButtonDTO:
    """
    С TL-слоя Telethon 1.45 вид кнопки лежит в её поле `type`.

    :param button: MessageButton из Telethon.
    :return: Кнопка в терминах предметной области.
    """
    kind = getattr(button.button, "type", None)
    if isinstance(kind, types.InlineButtonTypeCallback):
        return ButtonDTO(text=button.text, kind=ButtonKind.CALLBACK, requires_password=bool(kind.requires_password))
    if isinstance(kind, types.ButtonTypeDefault):
        return ButtonDTO(text=button.text, kind=ButtonKind.TEXT)
    if isinstance(kind, types.InlineButtonTypeUrl):
        return ButtonDTO(text=button.text, kind=ButtonKind.URL, url=kind.url)
    return ButtonDTO(text=button.text, kind=ButtonKind.OTHER, detail=type(kind).__name__)


def to_message_dto(message: Any) -> MessageDTO:
    file = message.file
    sender = None if message.out or message.sender is None else utils.get_display_name(message.sender) or None
    return MessageDTO(
        id=message.id,
        chat_id=message.chat_id,
        outgoing=bool(message.out),
        sender=sender,
        date=message.date,
        edit_date=message.edit_date,
        text=message.message or "",
        file=FileDTO(name=file.name, mime=file.mime_type, size=file.size) if file else None,
        buttons=tuple(tuple(to_button_dto(button) for button in row) for row in (message.buttons or [])),
    )


def parse_chat_ref(ref: str) -> str | int:
    """
    Чат указывается как @username, username или числовой id (в том числе -100…).

    :param ref: Ссылка на чат.
    :return: Числовой id или юзернейм без @.
    """
    value = ref.strip()
    if value.lstrip("-").isdigit():
        return int(value)
    return value.lstrip("@")

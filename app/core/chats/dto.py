from dataclasses import dataclass
from datetime import datetime

from app.core.chats.constants import ButtonKind, ChatKind


@dataclass(slots=True, frozen=True)
class ButtonDTO:
    text: str
    kind: ButtonKind
    url: str | None = None
    # Имя типа кнопки Telegram для kind=OTHER, чтобы было видно, что это
    detail: str | None = None
    requires_password: bool = False


@dataclass(slots=True, frozen=True)
class FileDTO:
    name: str | None
    mime: str | None
    size: int | None


@dataclass(slots=True, frozen=True)
class MessageDTO:
    """
    Сообщение сравнивается по значению: правка текста или клавиатуры
    делает его неравным прежнему, на этом строится ожидание ответа бота.
    """

    id: int
    chat_id: int
    outgoing: bool
    sender: str | None
    date: datetime
    edit_date: datetime | None
    text: str
    file: FileDTO | None = None
    buttons: tuple[tuple[ButtonDTO, ...], ...] = ()


@dataclass(slots=True, frozen=True)
class ChatDTO:
    id: int
    title: str
    kind: ChatKind
    username: str | None = None
    unread: int | None = None
    last_message_date: datetime | None = None


@dataclass(slots=True, frozen=True)
class SearchHitDTO:
    chat: ChatDTO | None
    message: MessageDTO

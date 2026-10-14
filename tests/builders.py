from datetime import UTC, datetime

from app.core.chats.constants import ButtonKind, ChatKind
from app.core.chats.dto import ButtonDTO, ChatDTO, MessageDTO

BASE_DATE = datetime(2026, 10, 14, 11, 0, tzinfo=UTC)


def build_button(
    text: str,
    kind: ButtonKind = ButtonKind.CALLBACK,
    *,
    url: str | None = None,
    detail: str | None = None,
    requires_password: bool = False,
) -> ButtonDTO:
    return ButtonDTO(text=text, kind=kind, url=url, detail=detail, requires_password=requires_password)


def build_message(
    message_id: int,
    text: str = "",
    *,
    outgoing: bool = False,
    buttons: tuple[tuple[ButtonDTO, ...], ...] = (),
    edited: bool = False,
    chat_id: int = 100,
) -> MessageDTO:
    return MessageDTO(
        id=message_id,
        chat_id=chat_id,
        outgoing=outgoing,
        sender=None if outgoing else "SpecFlow",
        date=BASE_DATE,
        edit_date=BASE_DATE if edited else None,
        text=text,
        buttons=buttons,
    )


def build_chat(
    chat_id: int = 100, title: str = "SpecFlow", kind: ChatKind = ChatKind.BOT, username: str | None = "specflowbot"
) -> ChatDTO:
    return ChatDTO(id=chat_id, title=title, kind=kind, username=username)

from typing import Any

from pydantic import BaseModel, Field

from app.core.bots.constants import PRESSABLE_KINDS
from app.core.chats.constants import ButtonKind
from app.core.chats.dto import ButtonDTO, ChatDTO, FileDTO, MessageDTO, SearchHitDTO


def button_label(button: ButtonDTO) -> str:
    """
    Подпись кнопки для модели: по ней же кнопку потом нажимают в tg_bot_press.

    :param button: Кнопка.
    :return: Текст кнопки с пометкой, если она не нажимается.
    """
    if button.kind in PRESSABLE_KINDS and not button.requires_password:
        return button.text
    if button.kind is ButtonKind.URL:
        return f"{button.text} [ссылка: {button.url}]"
    return f"{button.text} [{button.detail or button.kind.value}, не нажимается]"


class FileSerializer(BaseModel):
    name: str | None = Field(description="File name")
    mime: str | None = Field(description="MIME type")
    size: int | None = Field(description="Size in bytes")

    @classmethod
    def from_dto(cls, dto: FileDTO) -> "FileSerializer":
        return cls(name=dto.name, mime=dto.mime, size=dto.size)


class MessageSerializer(BaseModel):
    id: int = Field(description="Message id; use it for tg_bot_press and before_id")
    sender: str = Field(description="'me' for own messages, otherwise sender name")
    date: str = Field(description="ISO date")
    edited: bool = Field(description="Message was edited")
    text: str
    file: FileSerializer | None = None
    buttons: list[list[str]] | None = Field(default=None, description="Button rows; labels are used to press")

    @classmethod
    def from_dto(cls, dto: MessageDTO) -> "MessageSerializer":
        return cls(
            id=dto.id,
            sender="me" if dto.outgoing else (dto.sender or "unknown"),
            date=dto.date.isoformat(timespec="seconds"),
            edited=dto.edit_date is not None,
            text=dto.text,
            file=FileSerializer.from_dto(dto.file) if dto.file else None,
            buttons=[[button_label(button) for button in row] for row in dto.buttons] or None,
        )

    def dump(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ChatSerializer(BaseModel):
    id: int = Field(description="Chat id; can be passed as chat to tg_messages")
    title: str
    kind: str = Field(description="user | bot | group | channel")
    username: str | None = None
    unread: int | None = None
    last_message_date: str | None = None

    @classmethod
    def from_dto(cls, dto: ChatDTO) -> "ChatSerializer":
        return cls(
            id=dto.id,
            title=dto.title,
            kind=dto.kind.value,
            username=dto.username,
            unread=dto.unread,
            last_message_date=dto.last_message_date.isoformat(timespec="seconds") if dto.last_message_date else None,
        )

    def dump(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class SearchHitSerializer(BaseModel):
    chat: ChatSerializer | None
    message: MessageSerializer

    @classmethod
    def from_dto(cls, dto: SearchHitDTO) -> "SearchHitSerializer":
        return cls(
            chat=ChatSerializer.from_dto(dto.chat) if dto.chat else None,
            message=MessageSerializer.from_dto(dto.message),
        )

    def dump(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

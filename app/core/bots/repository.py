from dataclasses import dataclass

from app.core.bots.constants import PRESSABLE_KINDS
from app.core.bots.exceptions import BotMessageNotFound, ButtonNotPressable
from app.core.chats.dto import ChatDTO, MessageDTO
from app.core.chats.exceptions import ChatNotFound
from app.infra.adapters.telegram import (
    ENTITY_NOT_FOUND_ERRORS,
    TelegramClientProvider,
    to_button_dto,
    to_chat_dto,
    to_message_dto,
)


@dataclass(slots=True, frozen=True)
class BotsRepository:
    """
    Действия в чате с ботом через Telethon. Бот указывается юзернеймом:
    Telethon кэширует его после первого разрешения.
    """

    client_provider: TelegramClientProvider

    async def resolve(self, username: str) -> ChatDTO:
        client = await self.client_provider.get()
        try:
            entity = await client.get_entity(username)
        except ENTITY_NOT_FOUND_ERRORS:
            raise ChatNotFound(chat=f"@{username}") from None
        return to_chat_dto(entity)

    async def recent(self, username: str, limit: int) -> tuple[MessageDTO, ...]:
        client = await self.client_provider.get()
        found = await client.get_messages(username, limit=limit)
        return tuple(to_message_dto(message) for message in reversed(found))

    async def get(self, username: str, message_id: int) -> MessageDTO | None:
        client = await self.client_provider.get()
        found = await client.get_messages(username, ids=message_id)
        return to_message_dto(found) if found is not None else None

    async def send_text(self, username: str, text: str) -> None:
        client = await self.client_provider.get()
        await client.send_message(username, text)

    async def click(self, username: str, message_id: int, row: int, column: int) -> None:
        client = await self.client_provider.get()
        message = await client.get_messages(username, ids=message_id)
        if message is None or not message.buttons:
            raise BotMessageNotFound(message_id=message_id)
        button = message.buttons[row][column]
        # Повторная проверка вида кнопки прямо перед нажатием: сервис уже проверил,
        # но клавиатура могла смениться между чтением и нажатием.
        dto = to_button_dto(button)
        if dto.kind not in PRESSABLE_KINDS or dto.requires_password:
            raise ButtonNotPressable(button=dto.text, kind=dto.detail or dto.kind.value)
        await button.click()

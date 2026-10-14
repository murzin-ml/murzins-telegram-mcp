from dataclasses import dataclass
from typing import Any

from app.core.chats.dto import ChatDTO, MessageDTO, SearchHitDTO
from app.core.chats.exceptions import ChatNotFound
from app.infra.adapters.telegram import (
    ENTITY_NOT_FOUND_ERRORS,
    TelegramClientProvider,
    parse_chat_ref,
    to_chat_dto,
    to_message_dto,
)


@dataclass(slots=True, frozen=True)
class ChatsRepository:
    """
    Чтение чатов через Telethon. Только чтение: сообщения не отмечаются
    прочитанными, ничего не отправляется.
    """

    client_provider: TelegramClientProvider

    async def dialogs(self, *, limit: int) -> tuple[ChatDTO, ...]:
        client = await self.client_provider.get()
        return tuple(
            [
                to_chat_dto(dialog.entity, unread=dialog.unread_count, last_message_date=dialog.date)
                async for dialog in client.iter_dialogs(limit=limit)
            ]
        )

    async def resolve(self, ref: str) -> ChatDTO:
        return to_chat_dto(await self._entity(ref))

    async def messages(
        self, *, chat_id: int, limit: int, before_id: int | None, search: str | None
    ) -> tuple[MessageDTO, ...]:
        client = await self.client_provider.get()
        entity = await self._entity(str(chat_id))
        found = await client.get_messages(entity, limit=limit, offset_id=before_id or 0, search=search or None)
        return tuple(to_message_dto(message) for message in reversed(found))

    async def search_global(self, *, query: str, limit: int) -> tuple[SearchHitDTO, ...]:
        client = await self.client_provider.get()
        found = await client.get_messages(None, search=query, limit=limit)
        return tuple(
            SearchHitDTO(chat=to_chat_dto(message.chat) if message.chat else None, message=to_message_dto(message))
            for message in found
        )

    async def _entity(self, ref: str) -> Any:
        client = await self.client_provider.get()
        parsed = parse_chat_ref(ref)
        try:
            return await client.get_entity(parsed)
        except ENTITY_NOT_FOUND_ERRORS:
            if not isinstance(parsed, int):
                raise ChatNotFound(chat=ref) from None
        # Числовой id может отсутствовать в кэше сущностей: загрузка диалогов его заполняет
        await client.get_dialogs()
        try:
            return await client.get_entity(parsed)
        except ENTITY_NOT_FOUND_ERRORS:
            raise ChatNotFound(chat=ref) from None

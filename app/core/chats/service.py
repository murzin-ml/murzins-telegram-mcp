from dataclasses import dataclass

from app.core.chats.constants import DIALOG_SCAN_LIMIT, MAX_LIMIT
from app.core.chats.dto import ChatDTO, MessageDTO, SearchHitDTO
from app.core.chats.exceptions import ChatDenied, EmptyQuery, ReadDisabled
from app.core.chats.repository import ChatsRepository


def _clamp(limit: int) -> int:
    return max(1, min(limit, MAX_LIMIT))


@dataclass(slots=True, frozen=True)
class ChatsService:
    repository: ChatsRepository
    read_enabled: bool
    denied_chats: frozenset[str]

    async def list_chats(self, *, query: str | None, limit: int) -> tuple[ChatDTO, ...]:
        """
        Диалоги аккаунта, свежие сверху. С запросом — фильтр по названию и юзернейму.

        :param query: Фрагмент названия или юзернейма.
        :param limit: Сколько чатов вернуть.
        :return: Чаты без закрытых настройкой.
        """
        self._ensure_enabled()
        chats = await self.repository.dialogs(limit=DIALOG_SCAN_LIMIT if query else _clamp(limit))
        visible = [chat for chat in chats if not self._denied(chat_id=chat.id, username=chat.username)]
        if query:
            needle = query.strip().casefold()
            visible = [
                chat
                for chat in visible
                if needle in chat.title.casefold() or (chat.username and needle in chat.username.casefold())
            ]
        return tuple(visible[: _clamp(limit)])

    async def read(
        self, *, chat: str, limit: int, before_id: int | None = None, search: str | None = None
    ) -> tuple[ChatDTO, tuple[MessageDTO, ...]]:
        """
        Сообщения чата, старые сверху. Сообщения не отмечаются прочитанными.

        :param chat: @username или id чата.
        :param limit: Сколько сообщений вернуть.
        :param before_id: Листать назад: сообщения старше этого id.
        :param search: Поиск по тексту внутри чата.
        :return: Чат и его сообщения.
        """
        self._ensure_enabled()
        target = await self.repository.resolve(chat)
        if self._denied(chat_id=target.id, username=target.username):
            raise ChatDenied(chat=chat)
        messages = await self.repository.messages(
            chat_id=target.id, limit=_clamp(limit), before_id=before_id, search=search
        )
        return target, messages

    async def search(self, *, query: str, chat: str | None, limit: int) -> tuple[SearchHitDTO, ...]:
        """
        Поиск по тексту: по всем чатам или внутри одного.

        :param query: Что искать.
        :param chat: Ограничить одним чатом.
        :param limit: Сколько совпадений вернуть.
        :return: Совпадения без закрытых чатов.
        """
        self._ensure_enabled()
        if not query.strip():
            raise EmptyQuery()
        if chat:
            target, messages = await self.read(chat=chat, limit=limit, search=query)
            return tuple(SearchHitDTO(chat=target, message=message) for message in messages)

        hits = await self.repository.search_global(query=query, limit=_clamp(limit))
        return tuple(
            hit
            for hit in hits
            if not self._denied(
                chat_id=hit.chat.id if hit.chat else hit.message.chat_id,
                username=hit.chat.username if hit.chat else None,
            )
        )

    def _ensure_enabled(self) -> None:
        if not self.read_enabled:
            raise ReadDisabled()

    def _denied(self, *, chat_id: int, username: str | None) -> bool:
        return str(chat_id) in self.denied_chats or (username or "").lower() in self.denied_chats

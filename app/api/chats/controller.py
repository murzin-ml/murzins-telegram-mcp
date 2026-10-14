from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from app.api.chats.constants import DESCRIPTION_CHATS, DESCRIPTION_MESSAGES, DESCRIPTION_SEARCH
from app.api.chats.serializers import ChatSerializer, MessageSerializer, SearchHitSerializer
from app.api.exceptions import tool_errors
from app.core.chats.service import ChatsService
from app.di.containers import DIContainer

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=True)


def register_tools(server: MCPServer, container: DIContainer) -> None:
    """
    Регистрирует инструменты чтения и поиска по чатам.

    :param server: MCP-сервер.
    :param container: Контейнер зависимостей.
    """
    chats_service: ChatsService = container.services.chats_service()

    @server.tool(name="tg_chats", title="Telegram chats", description=DESCRIPTION_CHATS, annotations=READ_ONLY)
    async def tg_chats(query: str | None = None, limit: int = 30) -> dict[str, Any]:
        """
        :param query: Фрагмент названия или юзернейма.
        :param limit: Сколько чатов вернуть, до 100.
        :return: Чаты.
        """
        async with tool_errors():
            chats = await chats_service.list_chats(query=query, limit=limit)
        return {"chats": [ChatSerializer.from_dto(chat).dump() for chat in chats]}

    @server.tool(name="tg_messages", title="Telegram messages", description=DESCRIPTION_MESSAGES, annotations=READ_ONLY)
    async def tg_messages(
        chat: str, limit: int = 30, before_id: int | None = None, search: str | None = None
    ) -> dict[str, Any]:
        """
        :param chat: @username или id чата.
        :param limit: Сколько сообщений вернуть, до 100.
        :param before_id: Сообщения старше этого id.
        :param search: Поиск по тексту внутри чата.
        :return: Чат и сообщения.
        """
        async with tool_errors():
            target, messages = await chats_service.read(chat=chat, limit=limit, before_id=before_id, search=search)
        return {
            "chat": ChatSerializer.from_dto(target).dump(),
            "messages": [MessageSerializer.from_dto(message).dump() for message in messages],
        }

    @server.tool(name="tg_search", title="Telegram search", description=DESCRIPTION_SEARCH, annotations=READ_ONLY)
    async def tg_search(query: str, chat: str | None = None, limit: int = 20) -> dict[str, Any]:
        """
        :param query: Что искать.
        :param chat: Ограничить одним чатом.
        :param limit: Сколько совпадений вернуть, до 100.
        :return: Совпадения.
        """
        async with tool_errors():
            hits = await chats_service.search(query=query, chat=chat, limit=limit)
        return {"hits": [SearchHitSerializer.from_dto(hit).dump() for hit in hits]}

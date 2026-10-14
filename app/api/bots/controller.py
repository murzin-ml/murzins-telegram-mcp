from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from app.api.bots.constants import DESCRIPTION_HISTORY, DESCRIPTION_PRESS, DESCRIPTION_SEND
from app.api.bots.serializers import BotReplySerializer
from app.api.chats.serializers import MessageSerializer
from app.api.exceptions import tool_errors
from app.core.bots.service import BotsService
from app.di.containers import DIContainer

ACTS_ON_BOT = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=True)


def register_tools(server: MCPServer, container: DIContainer) -> None:
    """
    Регистрирует инструменты работы с ботами.

    :param server: MCP-сервер.
    :param container: Контейнер зависимостей.
    """
    bots_service: BotsService = container.services.bots_service()

    @server.tool(
        name="tg_bot_history",
        title="Bot chat history",
        description=DESCRIPTION_HISTORY,
        annotations=ToolAnnotations(read_only_hint=True, open_world_hint=True),
    )
    async def tg_bot_history(bot: str, limit: int = 10) -> dict[str, Any]:
        """
        :param bot: Юзернейм бота, например specflowbot.
        :param limit: Сколько сообщений вернуть, до 50.
        :return: Сообщения чата.
        """
        async with tool_errors():
            messages = await bots_service.history(bot=bot, limit=limit)
        return {"messages": [MessageSerializer.from_dto(message).dump() for message in messages]}

    @server.tool(name="tg_bot_send", title="Send text to a bot", description=DESCRIPTION_SEND, annotations=ACTS_ON_BOT)
    async def tg_bot_send(bot: str, text: str) -> dict[str, Any]:
        """
        :param bot: Юзернейм бота.
        :param text: Текст или команда.
        :return: Ответ бота.
        """
        async with tool_errors():
            reply = await bots_service.send(bot=bot, text=text)
        return BotReplySerializer.from_dto(reply).dump()

    @server.tool(
        name="tg_bot_press", title="Press a bot button", description=DESCRIPTION_PRESS, annotations=ACTS_ON_BOT
    )
    async def tg_bot_press(bot: str, message_id: int, button: str) -> dict[str, Any]:
        """
        :param bot: Юзернейм бота.
        :param message_id: Id сообщения с кнопкой.
        :param button: Текст кнопки целиком или однозначный фрагмент.
        :return: Ответ бота или адрес ссылки.
        """
        async with tool_errors():
            reply = await bots_service.press(bot=bot, message_id=message_id, button=button)
        return BotReplySerializer.from_dto(reply).dump()

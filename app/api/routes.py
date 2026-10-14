from mcp.server import MCPServer

from app.api.bots.controller import register_tools as register_bots_tools
from app.api.chats.controller import register_tools as register_chats_tools
from app.di.containers import DIContainer


def register_tools(server: MCPServer, container: DIContainer) -> None:
    """
    Регистрирует инструменты. Чтение чатов подключается, только если оно
    включено в настройках: при выключенном модели эти инструменты даже не видны.

    :param server: MCP-сервер.
    :param container: Контейнер зависимостей.
    """
    register_bots_tools(server=server, container=container)
    if container.telegram_settings().TG_READ_ENABLED:
        register_chats_tools(server=server, container=container)

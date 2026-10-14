from mcp.server import MCPServer

from app.api.bots.controller import register_tools as register_bots_tools
from app.api.chats.controller import register_tools as register_chats_tools
from app.api.constants import INSTRUCTIONS_BASE, INSTRUCTIONS_READ_DISABLED, INSTRUCTIONS_READ_ENABLED
from app.di.containers import DIContainer


def server_instructions(*, read_enabled: bool) -> str:
    """
    Инструкции для модели. При выключенном чтении прямо говорят, как его включить:
    иначе модель видит только tg_bot_* и сочиняет неверные объяснения.

    :param read_enabled: Включено ли чтение чатов.
    :return: Текст инструкций.
    """
    return f"{INSTRUCTIONS_BASE} {INSTRUCTIONS_READ_ENABLED if read_enabled else INSTRUCTIONS_READ_DISABLED}"


def register_tools(server: MCPServer, container: DIContainer) -> None:
    """
    Регистрирует инструменты. Чтение чатов подключается, только если оно
    включено в настройках.

    :param server: MCP-сервер.
    :param container: Контейнер зависимостей.
    """
    register_bots_tools(server=server, container=container)
    if container.telegram_settings().TG_READ_ENABLED:
        register_chats_tools(server=server, container=container)

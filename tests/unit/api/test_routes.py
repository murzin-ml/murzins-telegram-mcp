from dependency_injector import providers

from app.di.containers import DIContainer
from app.main import create_server
from settings.telegram import TelegramSettings

BOT_TOOLS = {"tg_bot_history", "tg_bot_send", "tg_bot_press"}
READ_TOOLS = {"tg_chats", "tg_messages", "tg_search"}


def container_with(**settings: object) -> DIContainer:
    container = DIContainer()
    container.telegram_settings.override(providers.Object(TelegramSettings(**settings)))
    return container


async def tool_names(container: DIContainer) -> set[str]:
    server = create_server(container)
    return {tool.name for tool in await server.list_tools()}


async def test_read_tools_are_hidden_when_reading_is_disabled():
    assert await tool_names(container_with()) == BOT_TOOLS


async def test_read_tools_are_registered_when_reading_is_enabled():
    assert await tool_names(container_with(TG_READ_ENABLED=True)) == BOT_TOOLS | READ_TOOLS

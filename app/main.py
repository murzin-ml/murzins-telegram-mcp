from mcp.server import MCPServer

from app.api.constants import SERVER_INSTRUCTIONS, SERVER_NAME, SERVER_VERSION
from app.api.routes import register_tools
from app.di.containers import DIContainer
from app.infra.adapters.logging import configure_logging


def create_server(container: DIContainer | None = None) -> MCPServer:
    """
    Фабрика MCP-сервера. Контейнер можно передать заранее настроенным, например в тестах.

    :param container: Контейнер зависимостей.
    :return: Настроенный сервер.
    """
    container = container or DIContainer()
    server = MCPServer(name=SERVER_NAME, version=SERVER_VERSION, instructions=SERVER_INSTRUCTIONS)
    register_tools(server=server, container=container)
    return server


def main() -> None:
    container = DIContainer()
    configure_logging(level=container.app_settings().LOG_LEVEL)
    create_server(container).run(transport="stdio")


if __name__ == "__main__":
    main()

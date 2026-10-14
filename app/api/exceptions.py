from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.mcpserver.exceptions import ToolError
from telethon.errors import RPCError

from app.core.exceptions import MurzinsTelegramCoreException
from app.infra.exceptions import MurzinsTelegramInfraException


@asynccontextmanager
async def tool_errors() -> AsyncIterator[None]:
    """
    Переводит ожидаемые ошибки в ошибки уровня инструмента: так модель видит
    причину, а не общее «Error executing tool». Остальное SDK считает сбоем.
    """
    try:
        yield
    except (MurzinsTelegramCoreException, MurzinsTelegramInfraException) as exc:
        raise ToolError(str(exc)) from exc
    except RPCError as exc:
        raise ToolError(f"Telegram ответил ошибкой: {exc}") from exc

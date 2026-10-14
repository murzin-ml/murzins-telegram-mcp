import asyncio

import typer
from telethon import utils

from app.di.containers import DIContainer
from app.infra.adapters.secrets import save_secret
from app.infra.adapters.telegram import build_client
from app.infra.exceptions import MurzinsTelegramInfraException
from settings.constants import SECRETS_FILE


def run_login() -> None:
    """
    Интерактивный вход: телефон, код из Telegram и облачный пароль, если он включён.
    Строка сессии записывается в .env.local и на экран не выводится.
    """
    settings = DIContainer().telegram_settings()
    try:
        client = build_client(settings=settings, session="")
    except MurzinsTelegramInfraException as exc:
        typer.echo(f"Ошибка: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    async def login() -> str:
        await client.start()
        me = await client.get_me()
        save_secret(path=SECRETS_FILE, key="TG_SESSION", value=client.session.save())
        await client.disconnect()
        return utils.get_display_name(me)

    name = asyncio.run(login())
    typer.echo(f"Готово: вошли как {name}. Сессия сохранена в {SECRETS_FILE.name}.")
    typer.echo(f"Отключить доступ: Telegram → Настройки → Устройства → {settings.TG_DEVICE_MODEL}.")

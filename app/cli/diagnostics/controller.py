import asyncio

import typer

from app.core.diagnostics.service import DiagnosticsService
from app.di.containers import DIContainer


def _mark(ok: bool) -> str:
    return "ok" if ok else "НЕТ"


def run_doctor() -> None:
    """
    Печатает состояние окружения: какие настройки заданы и жива ли сессия.
    Значения секретов не выводятся.
    """
    service: DiagnosticsService = DIContainer().services.diagnostics_service()
    report = asyncio.run(service.check())

    typer.echo(f"файл .env.local:        {_mark(report.secrets_file_exists)}")
    typer.echo(f"ключи API:              {_mark(report.api_keys_set)}")
    typer.echo(f"сессия задана:          {_mark(report.session_set)}")
    typer.echo(f"сессия действует:       {_mark(report.session_valid)}")
    if report.account:
        typer.echo(f"аккаунт:                {report.account}")
    typer.echo(f"чтение чатов:           {'включено' if report.read_enabled else 'выключено'}")
    typer.echo(f"боты:                   {', '.join(report.allowed_bots) or 'любые (только боты)'}")
    typer.echo(f"закрытых чатов:         {report.denied_chats_count}")
    if report.error:
        typer.echo(f"ошибка:                 {report.error}", err=True)
        raise typer.Exit(code=1)

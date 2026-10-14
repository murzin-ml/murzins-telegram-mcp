import typer

from app.cli.auth.controller import run_login
from app.cli.diagnostics.controller import run_doctor
from app.cli.main.constants import APP_HELP, APP_NAME, HELP_DOCTOR, HELP_LOGIN
from app.infra.adapters.logging import configure_logging
from settings.app import AppSettings

app = typer.Typer(name=APP_NAME, help=APP_HELP, no_args_is_help=True, add_completion=False)
app.command("login", help=HELP_LOGIN)(run_login)
app.command("doctor", help=HELP_DOCTOR)(run_doctor)


def main() -> None:
    configure_logging(level=AppSettings().LOG_LEVEL)
    app()

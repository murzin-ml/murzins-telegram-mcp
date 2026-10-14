from typing import Any


class MurzinsTelegramInfraException(Exception):
    msg_template: str

    def __init__(self, **ctx: Any) -> None:
        super().__init__()
        self.ctx = ctx

    def __str__(self) -> str:
        return self.msg_template.format(**self.ctx)


class TelegramConfigError(MurzinsTelegramInfraException):
    msg_template = "не заданы {missing} в .env.local: ключи приложения берутся на https://my.telegram.org/apps"


class TelegramSessionError(MurzinsTelegramInfraException):
    msg_template = "нет действующей сессии Telegram: выполните `make login`"

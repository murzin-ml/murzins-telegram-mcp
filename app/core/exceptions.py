from typing import Any


class MurzinsTelegramCoreException(Exception):
    """
    Ошибка предметной области. Текст уходит модели как результат инструмента,
    поэтому пишется так, чтобы было понятно, что делать дальше.
    """

    msg_template: str

    def __init__(self, **ctx: Any) -> None:
        super().__init__()
        self.ctx = ctx

    def __str__(self) -> str:
        return self.msg_template.format(**self.ctx)

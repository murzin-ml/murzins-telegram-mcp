from dataclasses import dataclass

from app.core.chats.dto import MessageDTO


@dataclass(slots=True, frozen=True)
class BotReplyDTO:
    # Новые и изменённые сообщения бота после действия
    updates: tuple[MessageDTO, ...] = ()
    # Бот не закончил отвечать за отведённое время
    timed_out: bool = False
    # Адрес кнопки-ссылки: сервер её не открывает, а только показывает
    url: str | None = None

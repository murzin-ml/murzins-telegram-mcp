from enum import StrEnum
from typing import Final


class ChatKind(StrEnum):
    USER = "user"
    BOT = "bot"
    GROUP = "group"
    CHANNEL = "channel"


class ButtonKind(StrEnum):
    # Колбэк инлайн-клавиатуры
    CALLBACK = "callback"
    # Простая кнопка reply-клавиатуры: нажать — значит отправить её текст
    TEXT = "text"
    URL = "url"
    # Оплата, запрос телефона/геолокации, мини-приложения и прочее
    OTHER = "other"


MAX_LIMIT: Final[int] = 100
# Сколько диалогов просматривать при поиске чата по названию
DIALOG_SCAN_LIMIT: Final[int] = 500

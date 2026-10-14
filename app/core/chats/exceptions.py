from app.core.exceptions import MurzinsTelegramCoreException


class ChatsServiceError(MurzinsTelegramCoreException):
    pass


class ReadDisabled(ChatsServiceError):
    msg_template = "чтение чатов выключено: включите TG_READ_ENABLED=true в .env.local"


class ChatDenied(ChatsServiceError):
    msg_template = "чат {chat} закрыт для чтения настройкой TG_READ_DENIED_CHATS"


class ChatNotFound(ChatsServiceError):
    msg_template = "чат {chat} не найден: укажите название чата, @username или id из tg_chats"


class ChatAmbiguous(ChatsServiceError):
    msg_template = "под «{chat}» подходит несколько чатов: {options}; уточните название или укажите id из tg_chats"


class EmptyQuery(ChatsServiceError):
    msg_template = "пустой поисковый запрос"

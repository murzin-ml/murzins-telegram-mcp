from app.core.exceptions import MurzinsTelegramCoreException


class BotsServiceError(MurzinsTelegramCoreException):
    pass


class NotABotUsername(BotsServiceError):
    msg_template = "«{bot}» не похоже на юзернейм бота: он должен заканчиваться на bot"


class BotNotAllowed(BotsServiceError):
    msg_template = "@{bot} нет в TG_ALLOWED_BOTS"


class NotABot(BotsServiceError):
    msg_template = "@{bot} — не бот, доступ закрыт"


class BotMessageNotFound(BotsServiceError):
    msg_template = "сообщение бота id={message_id} не найдено"


class ButtonNotFound(BotsServiceError):
    msg_template = "кнопка «{button}» не найдена однозначно; есть: {options}"


class ButtonNotPressable(BotsServiceError):
    msg_template = "кнопка «{button}» ({kind}) не нажимается: разрешены только обычные кнопки"

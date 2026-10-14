import re
from typing import Final

from app.core.chats.constants import ButtonKind

# Юзернейм бота по правилам Telegram: 5–32 символа и окончание на «bot»
BOT_USERNAME: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]{1,28}bot$")

# Нажимаются только обычные кнопки. Ссылка возвращает адрес и ничего не открывает;
# оплата, запрос телефона и геолокации, мини-приложения не нажимаются никогда.
PRESSABLE_KINDS: Final[frozenset[ButtonKind]] = frozenset({ButtonKind.CALLBACK, ButtonKind.TEXT})

MAX_HISTORY: Final[int] = 50
# Сколько последних сообщений сравнивать, чтобы заметить ответ или правку бота
SNAPSHOT_SIZE: Final[int] = 15
POLL_INTERVAL_SEC: Final[float] = 1.5

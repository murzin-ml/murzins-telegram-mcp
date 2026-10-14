import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.core.bots.constants import BOT_USERNAME, MAX_HISTORY, POLL_INTERVAL_SEC, PRESSABLE_KINDS, SNAPSHOT_SIZE
from app.core.bots.dto import BotReplyDTO
from app.core.bots.exceptions import (
    BotMessageNotFound,
    BotNotAllowed,
    ButtonNotFound,
    ButtonNotPressable,
    NotABot,
    NotABotUsername,
)
from app.core.bots.repository import BotsRepository
from app.core.chats.constants import ButtonKind, ChatKind
from app.core.chats.dto import ButtonDTO, MessageDTO


def find_button(message: MessageDTO, label: str) -> tuple[int, int, ButtonDTO]:
    """
    Ищет кнопку по тексту: сначала точное совпадение, затем однозначный фрагмент.

    :param message: Сообщение бота.
    :param label: Текст кнопки целиком или фрагментом.
    :return: Строка, столбец и сама кнопка.
    """
    positioned = [
        (row_index, column_index, button)
        for row_index, row in enumerate(message.buttons)
        for column_index, button in enumerate(row)
    ]
    wanted = label.strip().casefold()
    exact = [item for item in positioned if item[2].text.strip().casefold() == wanted]
    if len(exact) == 1:
        return exact[0]
    partial = [item for item in positioned if wanted in item[2].text.casefold()]
    if len(partial) == 1:
        return partial[0]

    options = ", ".join(f"«{button.text}»" for _, _, button in positioned) or "кнопок нет"
    raise ButtonNotFound(button=label, options=options)


@dataclass(slots=True, frozen=True)
class BotsService:
    """
    Работа с Telegram-ботами от аккаунта пользователя. С людьми, группами
    и каналами не работает: всё, что не бот, отклоняется до любого действия.
    """

    repository: BotsRepository
    allowed_bots: frozenset[str]
    reply_timeout_sec: float
    quiet_period_sec: float
    poll_interval_sec: float = POLL_INTERVAL_SEC
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    monotonic: Callable[[], float] = time.monotonic

    async def history(self, *, bot: str, limit: int) -> tuple[MessageDTO, ...]:
        username = await self._authorize(bot)
        return await self.repository.recent(username, max(1, min(limit, MAX_HISTORY)))

    async def send(self, *, bot: str, text: str) -> BotReplyDTO:
        username = await self._authorize(bot)
        return await self._act_and_wait(username, lambda: self.repository.send_text(username, text))

    async def press(self, *, bot: str, message_id: int, button: str) -> BotReplyDTO:
        """
        Нажимает обычную кнопку и ждёт результата. Кнопка-ссылка возвращает адрес
        без открытия; остальные виды кнопок отклоняются.

        :param bot: Юзернейм бота.
        :param message_id: Id сообщения с кнопкой.
        :param button: Текст кнопки целиком или однозначный фрагмент.
        :return: Ответ бота или адрес ссылки.
        """
        username = await self._authorize(bot)
        message = await self.repository.get(username, message_id)
        if message is None or message.outgoing:
            raise BotMessageNotFound(message_id=message_id)

        row, column, target = find_button(message, button)
        if target.kind is ButtonKind.URL:
            return BotReplyDTO(url=target.url)
        if target.kind not in PRESSABLE_KINDS or target.requires_password:
            raise ButtonNotPressable(button=target.text, kind=target.detail or target.kind.value)

        return await self._act_and_wait(username, lambda: self.repository.click(username, message_id, row, column))

    async def _authorize(self, bot: str) -> str:
        username = bot.strip().lstrip("@").lower()
        if not BOT_USERNAME.match(username):
            raise NotABotUsername(bot=bot)
        if self.allowed_bots and username not in self.allowed_bots:
            raise BotNotAllowed(bot=username)
        peer = await self.repository.resolve(username)
        if peer.kind is not ChatKind.BOT:
            raise NotABot(bot=username)
        return username

    async def _snapshot(self, username: str) -> dict[int, MessageDTO]:
        recent = await self.repository.recent(username, SNAPSHOT_SIZE)
        return {message.id: message for message in recent if not message.outgoing}

    async def _act_and_wait(self, username: str, action: Callable[[], Awaitable[None]]) -> BotReplyDTO:
        """
        Выполняет действие и собирает ответ. Бот может прислать несколько сообщений
        или долго править одно (потоковый вывод LLM), поэтому ждём, пока изменения
        не стихнут на quiet_period_sec. Сравнение идёт по значению DTO.
        """
        previous = await self._snapshot(username)
        await action()

        deadline = self.monotonic() + self.reply_timeout_sec
        changed: set[int] = set()
        last_change = self.monotonic()
        finished = False

        while self.monotonic() < deadline:
            await self.sleep(self.poll_interval_sec)
            current = await self._snapshot(username)
            activity = {message_id for message_id, message in current.items() if previous.get(message_id) != message}
            previous = current
            if activity:
                changed |= activity
                last_change = self.monotonic()
            elif changed and self.monotonic() - last_change >= self.quiet_period_sec:
                finished = True
                break

        updates = tuple(previous[message_id] for message_id in sorted(changed) if message_id in previous)
        return BotReplyDTO(updates=updates, timed_out=not finished)

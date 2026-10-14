from dataclasses import dataclass, field

from app.core.chats.dto import ChatDTO, MessageDTO, SearchHitDTO
from app.core.chats.exceptions import ChatNotFound


@dataclass
class FakeClock:
    now: float = 0.0

    def monotonic(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.now += seconds


@dataclass
class FakeBotsRepository:
    """
    timeline — последовательность состояний чата: каждый вызов recent() отдаёт
    следующее состояние, последнее повторяется.
    """

    peers: dict[str, ChatDTO]
    timeline: list[tuple[MessageDTO, ...]]
    sent: list[str] = field(default_factory=list)
    clicks: list[tuple[int, int, int]] = field(default_factory=list)
    _calls: int = 0

    async def resolve(self, username: str) -> ChatDTO:
        if username not in self.peers:
            raise ChatNotFound(chat=f"@{username}")
        return self.peers[username]

    async def recent(self, username: str, limit: int) -> tuple[MessageDTO, ...]:
        state = self.timeline[min(self._calls, len(self.timeline) - 1)]
        self._calls += 1
        return state[-limit:]

    async def get(self, username: str, message_id: int) -> MessageDTO | None:
        state = self.timeline[min(self._calls, len(self.timeline) - 1)]
        return next((message for message in state if message.id == message_id), None)

    async def send_text(self, username: str, text: str) -> None:
        self.sent.append(text)

    async def click(self, username: str, message_id: int, row: int, column: int) -> None:
        self.clicks.append((message_id, row, column))


@dataclass
class FakeChatsRepository:
    chats: list[ChatDTO]
    messages_by_chat: dict[int, tuple[MessageDTO, ...]] = field(default_factory=dict)
    global_hits: tuple[SearchHitDTO, ...] = ()

    async def dialogs(self, *, limit: int) -> tuple[ChatDTO, ...]:
        return tuple(self.chats[:limit])

    async def resolve(self, ref: str) -> ChatDTO:
        value = ref.strip().lstrip("@").lower()
        for chat in self.chats:
            if str(chat.id) == value or (chat.username or "").lower() == value:
                return chat
        raise ChatNotFound(chat=ref)

    async def messages(
        self, *, chat_id: int, limit: int, before_id: int | None, search: str | None
    ) -> tuple[MessageDTO, ...]:
        found = self.messages_by_chat.get(chat_id, ())
        if search:
            found = tuple(message for message in found if search.casefold() in message.text.casefold())
        return found[-limit:]

    async def search_global(self, *, query: str, limit: int) -> tuple[SearchHitDTO, ...]:
        return self.global_hits[:limit]

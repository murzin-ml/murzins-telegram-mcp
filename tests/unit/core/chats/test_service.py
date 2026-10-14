import pytest

from app.core.chats.constants import ChatKind
from app.core.chats.dto import SearchHitDTO
from app.core.chats.exceptions import ChatDenied, EmptyQuery, ReadDisabled
from app.core.chats.service import ChatsService
from tests.builders import build_chat, build_message
from tests.fakes import FakeChatsRepository

FRIEND = build_chat(1, "Алиса", ChatKind.USER, "alice_example")
WORK = build_chat(-1002, "Рабочий чат", ChatKind.GROUP, None)
BOT = build_chat(100, "SpecFlow", ChatKind.BOT, "specflowbot")


def make_service(
    *, enabled: bool = True, denied: frozenset[str] = frozenset()
) -> tuple[ChatsService, FakeChatsRepository]:
    repository = FakeChatsRepository(
        chats=[FRIEND, WORK, BOT],
        messages_by_chat={100: (build_message(1, "ТЗ готово"), build_message(2, "Оплата через CryptoBot"))},
        global_hits=(
            SearchHitDTO(chat=WORK, message=build_message(7, "оплата за спринт", chat_id=-1002)),
            SearchHitDTO(chat=None, message=build_message(8, "оплата", chat_id=1)),
        ),
    )
    return ChatsService(repository=repository, read_enabled=enabled, denied_chats=denied), repository


async def test_every_read_operation_refuses_when_reading_is_disabled():
    service, _ = make_service(enabled=False)
    with pytest.raises(ReadDisabled):
        await service.list_chats(query=None, limit=10)
    with pytest.raises(ReadDisabled):
        await service.read(chat="specflowbot", limit=10)
    with pytest.raises(ReadDisabled):
        await service.search(query="оплата", chat=None, limit=10)


async def test_list_hides_denied_chats_and_filters_by_query():
    service, _ = make_service(denied=frozenset({"-1002"}))
    assert [chat.title for chat in await service.list_chats(query=None, limit=10)] == ["Алиса", "SpecFlow"]
    assert [chat.title for chat in await service.list_chats(query="spec", limit=10)] == ["SpecFlow"]


async def test_read_refuses_chat_denied_by_username():
    service, _ = make_service(denied=frozenset({"alice_example"}))
    with pytest.raises(ChatDenied):
        await service.read(chat="@alice_example", limit=10)


async def test_search_inside_chat_filters_by_text():
    service, _ = make_service()
    hits = await service.search(query="cryptobot", chat="specflowbot", limit=10)
    assert [hit.message.id for hit in hits] == [2]


async def test_global_search_drops_denied_chats_even_without_chat_entity():
    service, _ = make_service(denied=frozenset({"-1002", "1"}))
    assert await service.search(query="оплата", chat=None, limit=10) == ()


async def test_search_rejects_empty_query():
    service, _ = make_service()
    with pytest.raises(EmptyQuery):
        await service.search(query="  ", chat=None, limit=10)

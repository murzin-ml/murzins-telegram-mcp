import pytest
from telethon.tl import types

from app.core.chats.constants import ChatKind
from app.core.chats.exceptions import ChatAmbiguous, ChatNotFound
from app.core.chats.repository import ChatsRepository
from tests.fakes import FakeClientProvider, FakeDialog, FakeTelegramClient


def group(chat_id: int, title: str) -> types.Channel:
    return types.Channel(id=chat_id, title=title, photo=types.ChatPhotoEmpty(), date=None, megagroup=True)


CLIENT_GROUP = group(11, "ГК РОСТ и Webant")
PUBLIC_WEBANT = types.User(id=99, bot=False, username="webant", first_name="Чужой аккаунт")


def repository(*dialogs: FakeDialog, usernames: dict | None = None) -> ChatsRepository:
    client = FakeTelegramClient(dialogs=list(dialogs), usernames=usernames or {})
    return ChatsRepository(client_provider=FakeClientProvider(client))


@pytest.mark.parametrize("ref", ["ГК РОСТ и Webant", "гк рост и webant", "рост"])
async def test_group_without_username_is_found_by_title(ref):
    chat = await repository(FakeDialog("ГК РОСТ и Webant", CLIENT_GROUP, id=-10011)).resolve(ref)
    assert (chat.title, chat.kind) == ("ГК РОСТ и Webant", ChatKind.GROUP)


async def test_own_chat_title_wins_over_public_username_with_same_word():
    repo = repository(FakeDialog("Webant", CLIENT_GROUP, id=-10011), usernames={"webant": PUBLIC_WEBANT})
    assert (await repo.resolve("Webant")).kind is ChatKind.GROUP
    assert (await repo.resolve("@webant")).title == "Чужой аккаунт"


async def test_ambiguous_title_lists_candidates_with_ids():
    repo = repository(
        FakeDialog("Проект А", group(1, "Проект А"), id=-1001), FakeDialog("Проект Б", group(2, "Проект Б"), id=-1002)
    )
    with pytest.raises(ChatAmbiguous) as error:
        await repo.resolve("проект")
    assert "-1001" in str(error.value)
    assert "-1002" in str(error.value)


async def test_unknown_title_is_reported_as_not_found():
    with pytest.raises(ChatNotFound):
        await repository(FakeDialog("ГК РОСТ и Webant", CLIENT_GROUP)).resolve("Нет такого чата")

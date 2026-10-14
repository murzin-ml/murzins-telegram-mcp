import pytest

from app.core.bots.exceptions import BotNotAllowed, ButtonNotFound, ButtonNotPressable, NotABot, NotABotUsername
from app.core.bots.service import BotsService
from app.core.chats.constants import ButtonKind, ChatKind
from tests.builders import build_button, build_chat, build_message
from tests.fakes import FakeBotsRepository, FakeClock

MENU = build_message(
    10,
    "Главное меню",
    buttons=(
        (build_button("🧠 Пройти интервью"),),
        (build_button("🆘 Поддержка", ButtonKind.URL, url="https://t.me/support"), build_button("👤 Профиль")),
        (build_button("📦 10 токенов — $5", ButtonKind.OTHER, detail="InlineButtonTypeBuy"),),
        (build_button("Передать бота", requires_password=True),),
    ),
)


def make_service(
    repository: FakeBotsRepository, clock: FakeClock, allowed: frozenset[str] = frozenset()
) -> BotsService:
    return BotsService(
        repository=repository,
        allowed_bots=allowed,
        reply_timeout_sec=30.0,
        quiet_period_sec=3.0,
        poll_interval_sec=1.0,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
    )


def bot_repository(*timeline: tuple) -> FakeBotsRepository:
    return FakeBotsRepository(peers={"specflowbot": build_chat()}, timeline=list(timeline))


@pytest.mark.parametrize("bot", ["durov", "+79991234567", "12345", "ab"])
async def test_rejects_usernames_that_are_not_bot_usernames(bot):
    service = make_service(bot_repository((MENU,)), FakeClock())
    with pytest.raises(NotABotUsername):
        await service.history(bot=bot, limit=5)


async def test_rejects_bot_outside_allowlist():
    service = make_service(bot_repository((MENU,)), FakeClock(), allowed=frozenset({"otherbot"}))
    with pytest.raises(BotNotAllowed):
        await service.history(bot="@SpecFlowBot", limit=5)


async def test_rejects_account_that_is_not_a_bot_even_with_bot_like_name():
    repository = FakeBotsRepository(
        peers={"sneakybot": build_chat(kind=ChatKind.USER, username="sneakybot")}, timeline=[(MENU,)]
    )
    with pytest.raises(NotABot):
        await make_service(repository, FakeClock()).history(bot="sneakybot", limit=5)


async def test_send_returns_new_reply_after_quiet_period():
    reply = build_message(11, "Вопрос 1/5")
    repository = bot_repository((MENU,), (MENU,), (MENU, reply), (MENU, reply))
    clock = FakeClock()

    result = await make_service(repository, clock).send(bot="specflowbot", text="/start")

    assert repository.sent == ["/start"]
    assert result.updates == (reply,)
    assert not result.timed_out
    assert clock.now < 30.0


async def test_send_follows_streaming_edits_and_returns_final_text():
    draft = build_message(11, "Анализирую")
    final = build_message(11, "Анализирую ответ полностью", edited=True)
    repository = bot_repository((MENU,), (MENU, draft), (MENU, final), (MENU, final))

    result = await make_service(repository, FakeClock()).send(bot="specflowbot", text="ответ")

    assert result.updates == (final,)


async def test_unchanged_old_messages_are_not_reported_as_updates():
    # Регрессия: раньше клавиатура сравнивалась через repr() с адресом в памяти,
    # и каждое старое сообщение с кнопками считалось изменённым.
    old = build_message(5, "старое", buttons=((build_button("◀ Назад"),),))
    repository = bot_repository((old, MENU), (old, MENU))

    result = await make_service(repository, FakeClock()).send(bot="specflowbot", text="/start")

    assert result.updates == ()
    assert result.timed_out


async def test_press_url_button_returns_address_without_clicking():
    repository = bot_repository((MENU,))
    result = await make_service(repository, FakeClock()).press(bot="specflowbot", message_id=10, button="Поддержка")

    assert result.url == "https://t.me/support"
    assert repository.clicks == []


@pytest.mark.parametrize("label", ["10 токенов", "Передать бота"])
async def test_press_refuses_payment_and_password_buttons(label):
    repository = bot_repository((MENU,))
    with pytest.raises(ButtonNotPressable):
        await make_service(repository, FakeClock()).press(bot="specflowbot", message_id=10, button=label)
    assert repository.clicks == []


async def test_press_clicks_callback_found_by_fragment():
    profile = build_message(10, "Ваш профиль", edited=True)
    repository = bot_repository((MENU,), (MENU,), (profile,), (profile,))

    result = await make_service(repository, FakeClock()).press(bot="specflowbot", message_id=10, button="профиль")

    assert repository.clicks == [(10, 1, 1)]
    assert result.updates == (profile,)


async def test_press_unknown_button_lists_available_options():
    with pytest.raises(ButtonNotFound) as error:
        await make_service(bot_repository((MENU,)), FakeClock()).press(bot="specflowbot", message_id=10, button="нет")
    assert "Пройти интервью" in str(error.value)

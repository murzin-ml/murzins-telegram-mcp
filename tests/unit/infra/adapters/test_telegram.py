from types import SimpleNamespace

import pytest
from telethon.tl import types

from app.core.chats.constants import ButtonKind, ChatKind
from app.infra.adapters.telegram import build_client, chat_kind, parse_chat_ref, to_button_dto
from app.infra.exceptions import TelegramConfigError
from settings.telegram import TelegramSettings


def inline(text: str, kind: object) -> SimpleNamespace:
    return SimpleNamespace(text=text, button=types.KeyboardInlineButton(text=text, type=kind))


def test_button_kinds_are_mapped_from_telethon_layer():
    callback = to_button_dto(inline("Профиль", types.InlineButtonTypeCallback(data=b"p")))
    url = to_button_dto(inline("Оплатить", types.InlineButtonTypeUrl(url="https://t.me/CryptoBot?start=x")))
    buy = to_button_dto(inline("Купить", types.InlineButtonTypeBuy()))
    password = to_button_dto(inline("Передать", types.InlineButtonTypeCallback(data=b"t", requires_password=True)))
    reply_text = to_button_dto(
        SimpleNamespace(text="Да", button=types.KeyboardButton(text="Да", type=types.ButtonTypeDefault()))
    )
    phone = to_button_dto(
        SimpleNamespace(
            text="Телефон", button=types.KeyboardButton(text="Телефон", type=types.ButtonTypeRequestPhone())
        )
    )

    assert callback.kind is ButtonKind.CALLBACK
    assert not callback.requires_password
    assert (url.kind, url.url) == (ButtonKind.URL, "https://t.me/CryptoBot?start=x")
    assert (buy.kind, buy.detail) == (ButtonKind.OTHER, "InlineButtonTypeBuy")
    assert password.requires_password
    assert reply_text.kind is ButtonKind.TEXT
    assert phone.kind is ButtonKind.OTHER


def test_chat_kind_tells_bots_from_people():
    assert chat_kind(types.User(id=1, bot=True)) is ChatKind.BOT
    assert chat_kind(types.User(id=2, bot=False)) is ChatKind.USER


@pytest.mark.parametrize(
    ("ref", "expected"),
    [("@specflowbot", "specflowbot"), ("specflowbot", "specflowbot"), ("12345", 12345), ("-1001234", -1001234)],
)
def test_parse_chat_ref(ref, expected):
    assert parse_chat_ref(ref) == expected


def test_client_is_not_built_without_api_keys():
    with pytest.raises(TelegramConfigError) as error:
        build_client(settings=TelegramSettings(), session="")
    assert "TG_API_ID" in str(error.value)
    assert "TG_API_HASH" in str(error.value)

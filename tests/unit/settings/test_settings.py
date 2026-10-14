from settings.telegram import TelegramSettings


def test_defaults_are_safe():
    settings = TelegramSettings()
    assert not settings.TG_READ_ENABLED
    assert settings.allowed_bots == frozenset()
    assert settings.denied_chats == frozenset()


def test_reference_lists_are_normalized():
    settings = TelegramSettings(
        TG_ALLOWED_BOTS=" @SpecFlowBot, otherbot ,", TG_READ_DENIED_CHATS="-1002,@Alice_Example"
    )
    assert settings.allowed_bots == frozenset({"specflowbot", "otherbot"})
    assert settings.denied_chats == frozenset({"-1002", "alice_example"})


def test_secrets_do_not_leak_through_repr():
    settings = TelegramSettings(TG_API_HASH="0123456789abcdef0123456789abcdef", TG_SESSION="1" + "A" * 350)
    assert "0123456789abcdef" not in repr(settings)
    assert "AAAA" not in repr(settings)

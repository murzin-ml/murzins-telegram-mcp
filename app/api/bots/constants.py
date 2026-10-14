from typing import Final

DESCRIPTION_HISTORY: Final[str] = (
    "Last messages in the chat with a bot, oldest first, with button labels and attached files. "
    "Only for chats with bot accounts; to read people, groups and channels use tg_messages."
)
DESCRIPTION_SEND: Final[str] = "Send a text message or command (e.g. /start) to a bot and wait for its reply."
DESCRIPTION_PRESS: Final[str] = (
    "Press a button under a bot message by its label (as shown in tg_bot_history) and wait for the result. "
    "Only regular buttons are pressed; URL buttons return their address, payment and other buttons are refused."
)

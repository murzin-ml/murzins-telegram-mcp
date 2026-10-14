from typing import Final

DESCRIPTION_CHATS: Final[str] = (
    "List the user's Telegram chats, most recent first, with unread counts. "
    "Optional query filters by title or username. Read-only."
)
DESCRIPTION_MESSAGES: Final[str] = (
    "Read messages of one chat, oldest first. chat is @username or id from tg_chats. "
    "before_id pages back; search filters by text. Does not mark messages as read."
)
DESCRIPTION_SEARCH: Final[str] = (
    "Search message text across all chats, or inside one chat when chat is given. Read-only."
)

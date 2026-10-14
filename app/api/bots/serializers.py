from typing import Any

from pydantic import BaseModel, Field

from app.api.chats.serializers import MessageSerializer
from app.core.bots.dto import BotReplyDTO


class BotReplySerializer(BaseModel):
    updates: list[MessageSerializer] = Field(description="New and edited bot messages after the action")
    timed_out: bool = Field(description="The bot had not finished replying when the wait ended")
    url: str | None = Field(default=None, description="Address of a URL button; it is not opened")

    @classmethod
    def from_dto(cls, dto: BotReplyDTO) -> "BotReplySerializer":
        return cls(
            updates=[MessageSerializer.from_dto(message) for message in dto.updates],
            timed_out=dto.timed_out,
            url=dto.url,
        )

    def dump(self) -> dict[str, Any]:
        if self.url is not None:
            return {"url": self.url, "note": "Это кнопка-ссылка, сервер её не открывает"}
        return {
            "updates": [message.dump() for message in self.updates],
            "timed_out": self.timed_out,
        }

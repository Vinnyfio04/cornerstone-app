"""Framework-free orchestration for persisted chat requests."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from backend.controllers.database_controller import DatabaseController
from backend.models import ChatLog

from .chat_provider import (
    ChatProvider,
    ChatTurn,
    ModelTimeoutError,
    ModelUnavailableError,
)


MAX_USER_MESSAGE_CHARS = 2_000
MAX_CONTEXT_MESSAGES = 12
MAX_CONTEXT_CHARS = 8_000
MAX_RESPONSE_CHARS = 4_000

FALLBACK_MESSAGE = (
    "I couldn't create a response right now. Your message was saved, and the "
    "breathing, grounding, history, and support pages remain available."
)


class ChatResourceNotFoundError(LookupError):
    """The requested user or conversation is unavailable to this request."""


@dataclass(frozen=True, slots=True)
class ChatResult:
    conversation_id: int
    user_message: ChatLog
    assistant_message: ChatLog
    chat_mode: str


class ChatService:
    def __init__(self, database: DatabaseController, provider: ChatProvider) -> None:
        self.database = database
        self.provider = provider

    @property
    def mode(self) -> str:
        return self.provider.mode

    @property
    def model_ready(self) -> bool:
        return self.provider.model_ready

    def send_message(
        self,
        user_id: int,
        content: str,
        conversation_id: int | None = None,
    ) -> ChatResult:
        content = content.strip()
        if not content or len(content) > MAX_USER_MESSAGE_CHARS:
            raise ValueError("Message content is outside the supported boundary")

        if self.database.get_user(user_id) is None:
            raise ChatResourceNotFoundError("User was not found")

        if conversation_id is None:
            conversation = self.database.create_conversation(user_id)
        else:
            conversation = self.database.get_conversation(conversation_id)
            if conversation is None or conversation.user_id != user_id:
                raise ChatResourceNotFoundError("Conversation was not found")

        user_message = self.database.create_chat_log(
            user_id,
            "user",
            content,
            conversation_id=conversation.id,
        )
        turns = self._bounded_context(
            self.database.list_conversation_chat_logs(conversation.id)
        )

        try:
            assistant_content = self.provider.generate(turns).strip()
            if not assistant_content:
                raise ModelUnavailableError("Provider returned no usable text")
            assistant_message = self.database.create_chat_log(
                user_id,
                "assistant",
                assistant_content[:MAX_RESPONSE_CHARS],
                conversation_id=conversation.id,
            )
        except (ModelTimeoutError, ModelUnavailableError):
            self.database.create_chat_log(
                user_id,
                "assistant",
                FALLBACK_MESSAGE,
                delivery_status="fallback",
                conversation_id=conversation.id,
            )
            raise

        return ChatResult(
            conversation_id=conversation.id,
            user_message=user_message,
            assistant_message=assistant_message,
            chat_mode=self.mode,
        )

    @staticmethod
    def _bounded_context(messages: Sequence[ChatLog]) -> list[ChatTurn]:
        selected: list[ChatTurn] = []
        remaining_chars = MAX_CONTEXT_CHARS

        for message in reversed(messages[-MAX_CONTEXT_MESSAGES:]):
            if remaining_chars <= 0:
                break
            content = message.content[:remaining_chars]
            selected.append(ChatTurn(role=message.role, content=content))
            remaining_chars -= len(content)

        selected.reverse()
        return selected

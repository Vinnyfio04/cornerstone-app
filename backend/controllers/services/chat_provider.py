"""Bounded OpenAI provider adapter for controller-owned chat."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from .chat_prompt import SYSTEM_INSTRUCTION


MAX_OUTPUT_TOKENS = 256
REQUEST_TIMEOUT_SECONDS = 15.0

@dataclass(frozen=True, slots=True)
class ChatTurn:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ProviderSettings:
    api_key: str | None = None
    model: str | None = None

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> "ProviderSettings":
        values = os.environ if environment is None else environment
        api_key = (
            values.get("OPENAI_API_KEY")
            or values.get("OPEN_AI_API_KEY")
            or ""
        ).strip() or None
        model = (
            values.get("OPENAI_CHAT_MODEL")
            or values.get("VOICE_BACKEND_MODEL")
            or ""
        ).strip() or None
        return cls(api_key=api_key, model=model)


class ModelUnavailableError(RuntimeError):
    """The configured provider cannot return a usable response."""


class ModelTimeoutError(RuntimeError):
    """The configured provider exceeded its request deadline."""


class ChatProvider(Protocol):
    mode: str

    @property
    def model_ready(self) -> bool: ...

    def generate(self, turns: Sequence[ChatTurn]) -> str: ...


class OpenAIChatProvider:
    """OpenAI Responses API adapter with server-only credentials and bounds."""

    mode = "openai"

    def __init__(self, api_key: str | None, model: str | None) -> None:
        self._api_key = api_key
        self._model = model

    @property
    def model_ready(self) -> bool:
        return bool(self._api_key and self._model)

    def generate(self, turns: Sequence[ChatTurn]) -> str:
        if not self.model_ready:
            raise ModelUnavailableError("OpenAI configuration is incomplete")

        input_messages = [
            {"role": turn.role, "content": turn.content}
            for turn in turns
            if turn.role in {"user", "assistant"}
        ]

        try:
            client = OpenAI(
                api_key=self._api_key,
                timeout=REQUEST_TIMEOUT_SECONDS,
                max_retries=0,
            )
            response = client.responses.create(
                model=self._model,
                instructions=SYSTEM_INSTRUCTION,
                input=input_messages,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                store=False,
            )
            text = (response.output_text or "").strip()
        except APITimeoutError as error:
            raise ModelTimeoutError("OpenAI request timed out") from error
        except APIStatusError as error:
            if error.status_code in {408, 504}:
                raise ModelTimeoutError("OpenAI request timed out") from error
            raise ModelUnavailableError("OpenAI request failed") from error
        except APIConnectionError as error:
            raise ModelUnavailableError("OpenAI request failed") from error
        except Exception as error:
            if isinstance(error, TimeoutError) or "timeout" in type(error).__name__.lower():
                raise ModelTimeoutError("OpenAI request timed out") from error
            raise ModelUnavailableError("OpenAI request failed") from error

        if not text:
            raise ModelUnavailableError("OpenAI returned no usable text")
        return text


def build_chat_provider(settings: ProviderSettings) -> ChatProvider:
    return OpenAIChatProvider(settings.api_key, settings.model)

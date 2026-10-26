"""Bounded mock and OpenAI provider adapters for controller-owned chat."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI


MAX_OUTPUT_TOKENS = 256
REQUEST_TIMEOUT_SECONDS = 15.0

SYSTEM_INSTRUCTION = (
    "Cornerstone is a coursework prototype, not therapy, diagnosis, monitoring, "
    "or an emergency service. Respond to fictional scenarios with calm, respectful, "
    "concise language. Do not diagnose, claim that anyone is monitoring the user, "
    "or invent crisis contact information. You may suggest the application's "
    "deterministic breathing or 5-4-3-2-1 grounding exercises."
)

MOCK_RESPONSE = (
    "Thanks for sharing that fictional scenario. You can take this one step at a "
    "time. If it helps, return to the breathing or 5-4-3-2-1 grounding exercise."
)


@dataclass(frozen=True, slots=True)
class ChatTurn:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ProviderSettings:
    mode: str = "mock"
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
        configured_mode = (values.get("CHAT_PROVIDER") or "").strip().lower()
        mode = configured_mode or ("openai" if api_key else "mock")
        if mode not in {"mock", "openai"}:
            raise ValueError("CHAT_PROVIDER must be 'mock' or 'openai'")
        return cls(mode=mode, api_key=api_key, model=model)


class ModelUnavailableError(RuntimeError):
    """The configured provider cannot return a usable response."""


class ModelTimeoutError(RuntimeError):
    """The configured provider exceeded its request deadline."""


class ChatProvider(Protocol):
    mode: str

    @property
    def model_ready(self) -> bool: ...

    def generate(self, turns: Sequence[ChatTurn]) -> str: ...


class MockChatProvider:
    """Deterministic provider used by default and in automated checks."""

    mode = "mock"

    def __init__(self, outcome: str = "success") -> None:
        if outcome not in {"success", "unavailable", "timeout"}:
            raise ValueError("Unsupported mock provider outcome")
        self.outcome = outcome

    @property
    def model_ready(self) -> bool:
        return False

    def generate(self, turns: Sequence[ChatTurn]) -> str:
        del turns
        if self.outcome == "timeout":
            raise ModelTimeoutError("Injected mock timeout")
        if self.outcome == "unavailable":
            raise ModelUnavailableError("Injected mock failure")
        return MOCK_RESPONSE


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
    if settings.mode == "mock":
        return MockChatProvider()
    return OpenAIChatProvider(settings.api_key, settings.model)

"""Server-owned OpenAI Live session creation for the voice controller boundary."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI


LIVE_MODEL = "gpt-live-1"
LIVE_REQUEST_TIMEOUT_SECONDS = 15.0
DEFAULT_VOICE_DURATION_SECONDS = 300
MIN_VOICE_DURATION_SECONDS = 30
MAX_VOICE_DURATION_SECONDS = 1_800
MAX_SDP_BYTES = 65_536

# The first View increment only needs session lifecycle and transcript events.
ALLOWED_CLIENT_EVENTS = ("session.close",)
ALLOWED_SERVER_EVENTS = (
    {"type": "session.started"},
    {"type": "session.input_transcript.delta"},
    {"type": "session.output_transcript.delta"},
    {"type": "session.closed"},
    {"type": "error"},
)

LIVE_INSTRUCTIONS = """You are Cornerstone's calm voice companion for short grounding conversations.
Speak warmly, naturally, and briefly at an unhurried pace. Ask one focused question at a time.

Backchannel policy: Use brief backchannels without competing with the user.

Interruption policy: Allow interruption; stop speaking and listen when the user interrupts.

Delegation policy:
Backend tools:
- Reviewed application knowledge and careful reasoning within Cornerstone's supported scope.

Generate <|SpawnThinking|> when:
- Reviewed application knowledge or careful reasoning is needed.

Do not generate <|SpawnThinking|> when:
- You can answer directly from the current conversation.
- You need a brief clarification.

Generate <|SpawnThinking|> before any answer that depends on backend work. Do not guess while waiting."""

DELEGATED_BACKEND_INSTRUCTIONS = """You are Cornerstone's delegated reasoning layer. Work only within the reviewed feature scope supplied by the application: supportive conversation about fictional scenarios, paced breathing, and 5-4-3-2-1 sensory grounding.

Treat statements about the user's experience as self-report. Clearly distinguish self-report from any tentative interpretation, and never state an inference as fact. Ask permission before suggesting an activity. If needed application or conversation context is missing, say what is missing honestly and ask one concise clarifying question when useful.

Do not diagnose, claim to provide therapy or treatment, give medical advice, imply human monitoring, or claim access to records or context the application did not supply. Do not control or replace the application's independent crisis-support route, and do not invent crisis resources. Return brief, grounded information for the voice model to communicate."""

_SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,254}$")


class VoiceUnavailableError(RuntimeError):
    """Voice is not configured or the provider did not return a usable session."""


class VoiceTimeoutError(RuntimeError):
    """The provider request exceeded its server-owned deadline."""


def validate_sdp(value: str) -> str:
    """Validate a bounded WebRTC SDP document without rewriting its line endings."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("SDP must not be blank")
    if "\x00" in value or len(value.encode("utf-8")) > MAX_SDP_BYTES:
        raise ValueError("SDP is invalid or too large")

    lines = [line.strip() for line in value.replace("\r\n", "\n").split("\n")]
    if not lines or lines[0] != "v=0":
        raise ValueError("SDP must begin with a version line")
    if not any(line.startswith("m=audio ") for line in lines):
        raise ValueError("SDP must contain an audio media section")
    return value


@dataclass(frozen=True, slots=True)
class VoiceSettings:
    """Environment-backed settings that are never serialized to the browser."""

    api_key: str | None = None
    backend_model: str | None = None
    duration_seconds: int = DEFAULT_VOICE_DURATION_SECONDS
    duration_valid: bool = True

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.backend_model and self.duration_valid)

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> "VoiceSettings":
        values = os.environ if environment is None else environment
        api_key = (
            values.get("OPENAI_API_KEY")
            or values.get("OPEN_AI_API_KEY")
            or ""
        ).strip() or None
        backend_model = (values.get("VOICE_BACKEND_MODEL") or "").strip() or None

        raw_duration = (values.get("VOICE_MAX_SESSION_SECONDS") or "").strip()
        duration = DEFAULT_VOICE_DURATION_SECONDS
        duration_valid = True
        if raw_duration:
            try:
                duration = int(raw_duration)
            except ValueError:
                duration_valid = False
                duration = DEFAULT_VOICE_DURATION_SECONDS
            else:
                duration_valid = (
                    MIN_VOICE_DURATION_SECONDS
                    <= duration
                    <= MAX_VOICE_DURATION_SECONDS
                )
                if not duration_valid:
                    duration = DEFAULT_VOICE_DURATION_SECONDS

        return cls(
            api_key=api_key,
            backend_model=backend_model,
            duration_seconds=duration,
            duration_valid=duration_valid,
        )


@dataclass(frozen=True, slots=True)
class VoiceSessionResult:
    session_id: str
    sdp_answer: str
    duration_seconds: int


class VoiceService:
    """Create validated Live sessions while keeping provider policy server-owned."""

    def __init__(
        self,
        settings: VoiceSettings,
        *,
        client_factory: Callable[..., Any] = OpenAI,
    ) -> None:
        self._settings = settings
        self._client_factory = client_factory

    @property
    def configured(self) -> bool:
        return self._settings.configured

    @property
    def duration_seconds(self) -> int:
        return self._settings.duration_seconds

    def create_session(self, sdp_offer: str) -> VoiceSessionResult:
        try:
            validated_offer = validate_sdp(sdp_offer)
        except ValueError as error:
            raise VoiceUnavailableError("Invalid SDP offer") from error

        if not self.configured:
            raise VoiceUnavailableError("Voice configuration is incomplete")

        try:
            client = self._client_factory(
                api_key=self._settings.api_key,
                timeout=LIVE_REQUEST_TIMEOUT_SECONDS,
                max_retries=0,
            )
            response = client.live.create(
                session={
                    "model": LIVE_MODEL,
                    "instructions": LIVE_INSTRUCTIONS,
                    "store": False,
                    "delegation": {
                        "type": "responses",
                        "responses": {
                            "model": self._settings.backend_model,
                            "instructions": DELEGATED_BACKEND_INSTRUCTIONS,
                            "tools": [],
                            "tool_choice": "none",
                            "parallel_tool_calls": False,
                            "max_output_tokens": 256,
                        },
                    },
                    "client": {
                        "data_channel": {
                            "allowed_client_events": list(ALLOWED_CLIENT_EVENTS),
                            "allowed_server_events": [
                                dict(event) for event in ALLOWED_SERVER_EVENTS
                            ],
                        }
                    },
                },
                transport={"type": "webrtc", "sdp": validated_offer},
            )
        except APITimeoutError as error:
            raise VoiceTimeoutError("Live session request timed out") from error
        except APIStatusError as error:
            if error.status_code in {408, 504}:
                raise VoiceTimeoutError("Live session request timed out") from error
            raise VoiceUnavailableError("Live session request failed") from error
        except APIConnectionError as error:
            raise VoiceUnavailableError("Live session request failed") from error
        except Exception as error:
            if isinstance(error, TimeoutError) or "timeout" in type(error).__name__.lower():
                raise VoiceTimeoutError("Live session request timed out") from error
            raise VoiceUnavailableError("Live session request failed") from error

        try:
            session_id = response.session.id
            transport = response.transport
            if transport.type != "webrtc":
                raise ValueError("Unexpected transport")
            sdp_answer = validate_sdp(transport.sdp)
            if not isinstance(session_id, str) or not _SESSION_ID_PATTERN.fullmatch(
                session_id
            ):
                raise ValueError("Invalid session ID")
        except (AttributeError, TypeError, ValueError) as error:
            raise VoiceUnavailableError("Live session response was invalid") from error

        return VoiceSessionResult(
            session_id=session_id,
            sdp_answer=sdp_answer,
            duration_seconds=self.duration_seconds,
        )

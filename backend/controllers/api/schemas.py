"""Validated request and response shapes for the Vue-facing JSON boundary."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.controllers.services.chat_service import MAX_USER_MESSAGE_CHARS
from backend.controllers.services.voice_service import MAX_SDP_BYTES, validate_sdp


class RequestModel(BaseModel):
    """Reject undocumented fields at the HTTP boundary."""

    model_config = ConfigDict(extra="forbid")


class UserCreateRequest(RequestModel):
    display_name: str = Field(min_length=1, max_length=100)
    preferences: dict[str, Any] = Field(default_factory=dict)

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be blank")
        return value


class UserUpdateRequest(RequestModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    preferences: dict[str, Any] | None = None

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_field_is_required(self) -> "UserUpdateRequest":
        if self.display_name is None and self.preferences is None:
            raise ValueError("At least one user field is required")
        return self


class ExerciseSessionCreateRequest(RequestModel):
    user_id: int = Field(gt=0)
    skill: Literal["paced_breathing", "sensory_grounding"]
    planned_duration_ms: int | None = Field(default=None, ge=0)


class ExerciseSessionUpdateRequest(RequestModel):
    status: Literal["completed", "exited"]
    measured_active_duration_ms: int = Field(ge=0)
    last_step: str | None = Field(default=None, max_length=100)


class ChatMessageRequest(RequestModel):
    user_id: int = Field(gt=0)
    conversation_id: int | None = Field(default=None, gt=0)
    content: str = Field(min_length=1, max_length=MAX_USER_MESSAGE_CHARS)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be blank")
        return value


class VoiceSessionRequest(RequestModel):
    sdp_offer: str = Field(min_length=1, max_length=MAX_SDP_BYTES)

    @field_validator("sdp_offer")
    @classmethod
    def sdp_offer_must_be_valid(cls, value: str) -> str:
        return validate_sdp(value)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiEnvelope(BaseModel):
    data: Any | None
    error: ErrorDetail | None

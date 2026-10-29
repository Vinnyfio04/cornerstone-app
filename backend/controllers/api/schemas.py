"""Validated request and response shapes for the Vue-facing JSON boundary."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.controllers.services.chat_service import MAX_USER_MESSAGE_CHARS
from backend.controllers.services.voice_service import MAX_SDP_BYTES, validate_sdp


class RequestModel(BaseModel):
    """Reject undocumented fields at the HTTP boundary."""

    model_config = ConfigDict(extra="forbid")


class UserCreateRequest(RequestModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    preferences: dict[str, Any] = Field(default_factory=dict)

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class UserUpdateRequest(RequestModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    preferences: dict[str, Any] | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_field_is_required(self) -> "UserUpdateRequest":
        if self.first_name is None and self.last_name is None and self.preferences is None:
            raise ValueError("At least one user field is required")
        return self


class AccountRegistrationRequest(RequestModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", "first_name", "last_name")
    @classmethod
    def account_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Account fields cannot be blank")
        return value


class AccountLoginRequest(RequestModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be blank")
        return value


class AccountUpdateRequest(RequestModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9._-]+$",
    )
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("username", "first_name", "last_name")
    @classmethod
    def optional_account_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Account fields cannot be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_account_field_is_required(self) -> "AccountUpdateRequest":
        if (
            self.username is None
            and self.first_name is None
            and self.last_name is None
            and self.password is None
        ):
            raise ValueError("At least one account field is required")
        return self


class ExerciseSessionCreateRequest(RequestModel):
    user_id: int = Field(gt=0)
    skill: Literal["paced_breathing", "sensory_grounding"]
    planned_duration_ms: int | None = Field(default=None, ge=0)


class ExerciseSessionUpdateRequest(RequestModel):
    status: Literal["completed", "exited"]
    measured_active_duration_ms: int = Field(ge=0)
    last_step: str | None = Field(default=None, max_length=100)


class CheckInCreateRequest(RequestModel):
    user_id: int = Field(gt=0)
    feeling: str = Field(min_length=1, max_length=50)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    description: str = Field(min_length=1, max_length=2_000)
    check_in_date: date

    @field_validator("feeling", "description")
    @classmethod
    def check_in_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Check-in text cannot be blank")
        return value


class CheckInUpdateRequest(RequestModel):
    feeling: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    description: str | None = Field(default=None, min_length=1, max_length=2_000)

    @field_validator("feeling", "description")
    @classmethod
    def optional_check_in_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Check-in text cannot be blank")
        return value

    @model_validator(mode="after")
    def at_least_one_check_in_field_is_required(self) -> "CheckInUpdateRequest":
        if self.feeling is None and self.color is None and self.description is None:
            raise ValueError("At least one check-in field is required")
        return self


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

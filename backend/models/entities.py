"""Framework-free model entities returned by backend controllers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    """Primary identity for locally persisted Cornerstone data."""

    id: int
    display_name: str
    preferences_json: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class Login:
    """A user's login record; password_hash must never contain plaintext."""

    id: int
    user_id: int
    username: str
    password_hash: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ChatLog:
    """One ordered conversation message associated with a user."""

    id: int
    user_id: int
    conversation_id: int
    role: str
    content: str
    delivery_status: str
    created_at: str


@dataclass(frozen=True, slots=True)
class Conversation:
    """A user-owned group of ordered chat messages."""

    id: int
    user_id: int
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ExerciseSession:
    """One measured breathing or sensory-grounding attempt."""

    id: int
    user_id: int
    skill: str
    status: str
    planned_duration_ms: int | None
    measured_active_duration_ms: int
    started_at: str
    ended_at: str | None
    last_step: str | None

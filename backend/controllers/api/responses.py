"""Stable JSON envelope and public entity serializers."""

from __future__ import annotations

import json
from typing import Any

from fastapi.responses import JSONResponse

from backend.controllers.services import AccountResult
from backend.models import CheckIn, ChatLog, Conversation, ExerciseSession, User


def success(data: Any) -> dict[str, Any]:
    return {"data": data, "error": None}


def failure(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {"code": code, "message": message},
        },
    )


def public_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "preferences": json.loads(user.preferences_json),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def public_account(account: AccountResult) -> dict[str, Any]:
    return {**public_user(account.user), "username": account.username}


def public_exercise_session(session: ExerciseSession) -> dict[str, Any]:
    return {
        "id": session.id,
        "user_id": session.user_id,
        "skill": session.skill,
        "status": session.status,
        "planned_duration_ms": session.planned_duration_ms,
        "measured_active_duration_ms": session.measured_active_duration_ms,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "last_step": session.last_step,
    }


def public_check_in(check_in: CheckIn) -> dict[str, Any]:
    return {
        "id": check_in.id,
        "user_id": check_in.user_id,
        "feeling": check_in.feeling,
        "color": check_in.color,
        "description": check_in.description,
        "check_in_date": check_in.check_in_date,
        "created_at": check_in.created_at,
    }


def public_conversation(conversation: Conversation) -> dict[str, Any]:
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


def public_chat_message(message: ChatLog) -> dict[str, Any]:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "delivery_status": message.delivery_status,
        "created_at": message.created_at,
    }

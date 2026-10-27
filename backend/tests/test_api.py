import json
import sqlite3

import pytest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.controllers.api import create_app
from backend.controllers.api.routes import (
    create_exercise_session,
    create_user,
    delete_user,
    get_health,
    get_user,
    list_conversation_messages,
    list_conversations,
    list_exercise_sessions,
    post_chat_message,
    update_exercise_session,
    update_user,
)
from backend.controllers.api.schemas import (
    ChatMessageRequest,
    ExerciseSessionCreateRequest,
    ExerciseSessionUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from backend.controllers.services import (
    ModelTimeoutError,
    ModelUnavailableError,
    ProviderSettings,
)


class FocusedChatProvider:
    """Focused provider double; production runtime has no mock response path."""

    mode = "openai"
    model_ready = True

    def __init__(self, outcome="success"):
        self.outcome = outcome

    def generate(self, turns):
        assert turns
        if self.outcome == "timeout":
            raise ModelTimeoutError("Injected test timeout")
        if self.outcome == "unavailable":
            raise ModelUnavailableError("Injected test failure")
        return "Focused fake response from the injected API test provider."


def response_body(response):
    if isinstance(response, JSONResponse):
        return json.loads(response.body)
    return response


@pytest.fixture
def api(tmp_path):
    application = create_app(
        tmp_path / "cornerstone-api-test.db",
        chat_provider=FocusedChatProvider(),
    )
    database = application.state.database_controller
    database.initialize_schema()
    return application, database


def create_fictional_user(database, name="Fictional Demo User"):
    return create_user(
        UserCreateRequest(
            display_name=name,
            preferences={"pace": "gentle"},
        ),
        database,
    )["data"]


def test_application_registers_documented_api_boundary(api):
    application, _ = api
    openapi = application.openapi()
    registered = {
        (method.upper(), path)
        for path, operations in openapi["paths"].items()
        for method in operations
    }

    assert {
        ("GET", "/api/health"),
        ("POST", "/api/users"),
        ("GET", "/api/users/{user_id}"),
        ("PATCH", "/api/users/{user_id}"),
        ("DELETE", "/api/users/{user_id}"),
        ("POST", "/api/exercise-sessions"),
        ("PATCH", "/api/exercise-sessions/{session_id}"),
        ("GET", "/api/users/{user_id}/exercise-sessions"),
        ("GET", "/api/users/{user_id}/conversations"),
        ("GET", "/api/conversations/{conversation_id}/messages"),
        ("POST", "/api/chat/messages"),
    } <= registered
    assert RequestValidationError in application.exception_handlers
    assert sqlite3.IntegrityError in application.exception_handlers
    assert sqlite3.DatabaseError in application.exception_handlers
    assert openapi["info"]["title"] == "Cornerstone API"


def test_health_uses_stable_envelope(api):
    application, _ = api
    assert get_health(application.state.chat_service) == {
        "data": {"status": "ok", "chat_mode": "openai", "model_ready": True},
        "error": None,
    }


def test_injected_provider_chat_endpoint_persists_a_conversation(api):
    application, database = api
    user = create_fictional_user(database, "Mock Chat User")

    response = post_chat_message(
        ChatMessageRequest(
            user_id=user["id"],
            conversation_id=None,
            content="A fictional situation for the injected provider.",
        ),
        application.state.chat_service,
    )

    assert response["error"] is None
    assert response["data"]["chat_mode"] == "openai"
    assert response["data"]["user_message"]["role"] == "user"
    assert response["data"]["assistant_message"]["role"] == "assistant"
    assert response["data"]["assistant_message"]["delivery_status"] == "delivered"
    messages = database.list_conversation_chat_logs(
        response["data"]["conversation_id"]
    )
    assert [message.role for message in messages] == ["user", "assistant"]


def test_unconfigured_production_chat_returns_fallback_instead_of_mock_success(tmp_path):
    application = create_app(
        tmp_path / "unconfigured-openai.db",
        provider_settings=ProviderSettings(),
    )
    database = application.state.database_controller
    database.initialize_schema()
    user = create_fictional_user(database, "Unconfigured OpenAI User")

    assert get_health(application.state.chat_service) == {
        "data": {"status": "ok", "chat_mode": "openai", "model_ready": False},
        "error": None,
    }
    response = post_chat_message(
        ChatMessageRequest(
            user_id=user["id"],
            conversation_id=None,
            content="This must not receive a synthetic successful reply.",
        ),
        application.state.chat_service,
    )

    assert response.status_code == 503
    assert response_body(response)["error"]["code"] == "model_unavailable"
    conversation = database.list_conversations(user["id"])[0]
    messages = database.list_conversation_chat_logs(conversation.id)
    assert [message.delivery_status for message in messages] == [
        "delivered",
        "fallback",
    ]


@pytest.mark.parametrize(
    ("outcome", "status_code", "error_code"),
    [
        ("unavailable", 503, "model_unavailable"),
        ("timeout", 504, "model_timeout"),
    ],
)
def test_chat_endpoint_maps_provider_failure_and_saves_fallback(
    tmp_path, outcome, status_code, error_code
):
    application = create_app(
        tmp_path / f"{outcome}.db",
        chat_provider=FocusedChatProvider(outcome),
    )
    database = application.state.database_controller
    database.initialize_schema()
    user = create_fictional_user(database, f"{outcome} User")

    response = post_chat_message(
        ChatMessageRequest(
            user_id=user["id"],
            conversation_id=None,
            content="Persist this fictional failure request.",
        ),
        application.state.chat_service,
    )

    assert response.status_code == status_code
    assert response_body(response)["error"]["code"] == error_code
    conversations = database.list_conversations(user["id"])
    messages = database.list_conversation_chat_logs(conversations[0].id)
    assert [message.delivery_status for message in messages] == [
        "delivered",
        "fallback",
    ]


def test_user_crud_and_request_validation(api):
    _, database = api
    user = create_fictional_user(database)

    assert set(user) == {
        "id",
        "display_name",
        "preferences",
        "created_at",
        "updated_at",
    }
    assert user["preferences"] == {"pace": "gentle"}
    assert get_user(user["id"], database)["data"]["id"] == user["id"]

    updated = update_user(
        user["id"],
        UserUpdateRequest(
            display_name="Updated Fictional User",
            preferences={"preferred_skill": "paced_breathing"},
        ),
        database,
    )
    assert updated["data"]["display_name"] == "Updated Fictional User"

    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate(
            {"display_name": "   ", "unexpected": "rejected"}
        )

    assert delete_user(user["id"], database) == {
        "data": {"deleted": True},
        "error": None,
    }
    missing = get_user(user["id"], database)
    assert missing.status_code == 404
    assert response_body(missing)["error"]["code"] == "not_found"


def test_exercise_lifecycle_history_and_conflict(api):
    _, database = api
    user = create_fictional_user(database, "Exercise API User")
    started = create_exercise_session(
        ExerciseSessionCreateRequest(
            user_id=user["id"],
            skill="paced_breathing",
            planned_duration_ms=60_000,
        ),
        database,
    )
    session = started["data"]

    assert session["status"] == "active"
    assert session["measured_active_duration_ms"] == 0
    assert session["ended_at"] is None
    with pytest.raises(ValidationError):
        ExerciseSessionCreateRequest(
            user_id=user["id"],
            skill="paced_breathing",
            planned_duration_ms=-1,
        )

    exited = update_exercise_session(
        session["id"],
        ExerciseSessionUpdateRequest(
            status="exited",
            measured_active_duration_ms=18_420,
            last_step="inhale_cycle_2",
        ),
        database,
    )
    repeated = update_exercise_session(
        session["id"],
        ExerciseSessionUpdateRequest(
            status="exited",
            measured_active_duration_ms=18_420,
            last_step="inhale_cycle_2",
        ),
        database,
    )
    conflict = update_exercise_session(
        session["id"],
        ExerciseSessionUpdateRequest(
            status="completed",
            measured_active_duration_ms=60_000,
            last_step="exhale_cycle_6",
        ),
        database,
    )

    assert exited["data"]["status"] == "exited"
    assert exited["data"]["measured_active_duration_ms"] == 18_420
    assert exited["data"]["ended_at"] is not None
    assert repeated["data"] == exited["data"]
    assert conflict.status_code == 409
    assert response_body(conflict)["error"]["code"] == "conflict"

    second = create_exercise_session(
        ExerciseSessionCreateRequest(
            user_id=user["id"],
            skill="sensory_grounding",
            planned_duration_ms=None,
        ),
        database,
    )["data"]
    history = list_exercise_sessions(user["id"], database)
    assert [item["id"] for item in history["data"]["sessions"]] == [
        second["id"],
        session["id"],
    ]


def test_conversation_history_is_public_and_ordered(api):
    _, database = api
    user = create_fictional_user(database, "Conversation API User")
    first_conversation = database.create_conversation(user["id"])
    second_conversation = database.create_conversation(user["id"])
    first_message = database.create_chat_log(
        user["id"],
        "user",
        "Fictional first message",
        conversation_id=first_conversation.id,
    )
    second_message = database.create_chat_log(
        user["id"],
        "assistant",
        "Bounded mock response",
        conversation_id=first_conversation.id,
    )

    conversations = list_conversations(user["id"], database)
    messages = list_conversation_messages(first_conversation.id, database)

    assert [item["id"] for item in conversations["data"]["conversations"]] == [
        second_conversation.id,
        first_conversation.id,
    ]
    assert [item["id"] for item in messages["data"]["messages"]] == [
        first_message.id,
        second_message.id,
    ]
    assert all(
        "user_id" not in item and "conversation_id" not in item
        for item in messages["data"]["messages"]
    )


def test_api_data_survives_application_restart(tmp_path):
    database_path = tmp_path / "restart-persistence.db"
    first_application = create_app(database_path)
    first_database = first_application.state.database_controller
    first_database.initialize_schema()
    user = create_fictional_user(first_database, "Restart User")
    session = create_exercise_session(
        ExerciseSessionCreateRequest(
            user_id=user["id"],
            skill="sensory_grounding",
            planned_duration_ms=None,
        ),
        first_database,
    )["data"]
    finished = update_exercise_session(
        session["id"],
        ExerciseSessionUpdateRequest(
            status="completed",
            measured_active_duration_ms=42_231,
            last_step="taste_1",
        ),
        first_database,
    )
    assert finished["data"]["status"] == "completed"

    second_application = create_app(database_path)
    second_database = second_application.state.database_controller
    second_database.initialize_schema()
    restored_user = get_user(user["id"], second_database)
    restored_history = list_exercise_sessions(user["id"], second_database)

    assert restored_user["data"]["display_name"] == "Restart User"
    restored_sessions = restored_history["data"]["sessions"]
    assert len(restored_sessions) == 1
    assert restored_sessions[0]["status"] == "completed"
    assert restored_sessions[0]["measured_active_duration_ms"] == 42_231
    assert restored_sessions[0]["last_step"] == "taste_1"

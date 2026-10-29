"""Thin FastAPI routes implementing the documented controller contract."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from backend.controllers.database_controller import DatabaseController
from backend.controllers.services import (
    AccountNotFoundError,
    AccountService,
    ChatResourceNotFoundError,
    ChatService,
    InvalidCredentialsError,
    ModelTimeoutError,
    ModelUnavailableError,
    VoiceService,
    VoiceTimeoutError,
    VoiceUnavailableError,
)

from .responses import (
    failure,
    public_account,
    public_check_in,
    public_chat_message,
    public_conversation,
    public_exercise_session,
    public_user,
    success,
)
from .schemas import (
    AccountLoginRequest,
    AccountRegistrationRequest,
    AccountUpdateRequest,
    ApiEnvelope,
    CheckInCreateRequest,
    CheckInUpdateRequest,
    ChatMessageRequest,
    ExerciseSessionCreateRequest,
    ExerciseSessionUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
    VoiceSessionRequest,
)


router = APIRouter(prefix="/api")


def get_database(request: Request) -> DatabaseController:
    return request.app.state.database_controller


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_account_service(request: Request) -> AccountService:
    return request.app.state.account_service


def get_voice_service(request: Request) -> VoiceService:
    return request.app.state.voice_service


DatabaseDependency = Annotated[DatabaseController, Depends(get_database)]
AccountServiceDependency = Annotated[AccountService, Depends(get_account_service)]
ChatServiceDependency = Annotated[ChatService, Depends(get_chat_service)]
VoiceServiceDependency = Annotated[VoiceService, Depends(get_voice_service)]


@router.get("/health", response_model=ApiEnvelope)
def get_health(chat_service: ChatServiceDependency) -> dict:
    return success(
        {
            "status": "ok",
            "chat_mode": chat_service.mode,
            "model_ready": chat_service.model_ready,
        }
    )


@router.post(
    "/accounts/register",
    response_model=ApiEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def register_account(
    payload: AccountRegistrationRequest,
    account_service: AccountServiceDependency,
) -> dict:
    account = account_service.register(
        payload.username,
        payload.first_name,
        payload.last_name,
        payload.password,
    )
    return success(public_account(account))


@router.post("/accounts/login", response_model=ApiEnvelope)
def login_account(
    payload: AccountLoginRequest,
    account_service: AccountServiceDependency,
):
    try:
        account = account_service.login(payload.username, payload.password)
    except InvalidCredentialsError:
        return failure(401, "invalid_credentials", "Username or password is incorrect.")
    return success(public_account(account))


@router.get("/accounts/{user_id}", response_model=ApiEnvelope)
def get_account(user_id: int, account_service: AccountServiceDependency):
    try:
        account = account_service.get(user_id)
    except AccountNotFoundError:
        return failure(404, "not_found", "Account was not found.")
    return success(public_account(account))


@router.patch("/accounts/{user_id}", response_model=ApiEnvelope)
def update_account(
    user_id: int,
    payload: AccountUpdateRequest,
    account_service: AccountServiceDependency,
):
    try:
        account = account_service.update(
            user_id,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password,
        )
    except AccountNotFoundError:
        return failure(404, "not_found", "Account was not found.")
    return success(public_account(account))


@router.delete("/accounts/{user_id}", response_model=ApiEnvelope)
def delete_account(user_id: int, account_service: AccountServiceDependency):
    try:
        account_service.delete(user_id)
    except AccountNotFoundError:
        return failure(404, "not_found", "Account was not found.")
    return success({"deleted": True})


@router.get("/voice/config", response_model=ApiEnvelope)
def get_voice_config(voice_service: VoiceServiceDependency) -> dict:
    return success(
        {
            "status": "configured" if voice_service.configured else "unconfigured",
            "duration_seconds": voice_service.duration_seconds,
        }
    )


@router.post(
    "/voice/sessions",
    response_model=ApiEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_voice_session(
    payload: VoiceSessionRequest,
    voice_service: VoiceServiceDependency,
):
    try:
        result = voice_service.create_session(payload.sdp_offer)
    except VoiceTimeoutError:
        return failure(
            504,
            "voice_timeout",
            "The voice session request timed out. Try again.",
        )
    except VoiceUnavailableError:
        return failure(
            503,
            "voice_unavailable",
            "Voice is temporarily unavailable. Try again.",
        )
    return success(
        {
            "session_id": result.session_id,
            "sdp_answer": result.sdp_answer,
            "duration_seconds": result.duration_seconds,
        }
    )


@router.post(
    "/users",
    response_model=ApiEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreateRequest, database: DatabaseDependency
) -> dict:
    user = database.create_user(
        payload.first_name,
        payload.last_name,
        payload.preferences,
    )
    return success(public_user(user))


@router.get("/users/{user_id}", response_model=ApiEnvelope)
def get_user(user_id: int, database: DatabaseDependency):
    user = database.get_user(user_id)
    if user is None:
        return failure(404, "not_found", "User was not found.")
    return success(public_user(user))


@router.patch("/users/{user_id}", response_model=ApiEnvelope)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    database: DatabaseDependency,
):
    user = database.update_user(
        user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        preferences=payload.preferences,
    )
    if user is None:
        return failure(404, "not_found", "User was not found.")
    return success(public_user(user))


@router.delete("/users/{user_id}", response_model=ApiEnvelope)
def delete_user(user_id: int, database: DatabaseDependency):
    if not database.delete_user(user_id):
        return failure(404, "not_found", "User was not found.")
    return success({"deleted": True})


@router.post(
    "/exercise-sessions",
    response_model=ApiEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise_session(
    payload: ExerciseSessionCreateRequest,
    database: DatabaseDependency,
):
    if database.get_user(payload.user_id) is None:
        return failure(404, "not_found", "User was not found.")
    session = database.create_exercise_session(
        payload.user_id,
        payload.skill,
        payload.planned_duration_ms,
    )
    return success(public_exercise_session(session))


@router.patch("/exercise-sessions/{session_id}", response_model=ApiEnvelope)
def update_exercise_session(
    session_id: int,
    payload: ExerciseSessionUpdateRequest,
    database: DatabaseDependency,
):
    if database.get_exercise_session(session_id) is None:
        return failure(404, "not_found", "Exercise session was not found.")
    try:
        session = database.update_exercise_session(
            session_id,
            status=payload.status,
            measured_active_duration_ms=payload.measured_active_duration_ms,
            last_step=payload.last_step,
        )
    except ValueError:
        return failure(409, "conflict", "Exercise session cannot be changed.")
    return success(public_exercise_session(session))


@router.get("/users/{user_id}/exercise-sessions", response_model=ApiEnvelope)
def list_exercise_sessions(user_id: int, database: DatabaseDependency):
    if database.get_user(user_id) is None:
        return failure(404, "not_found", "User was not found.")
    sessions = reversed(database.list_exercise_sessions(user_id))
    return success(
        {"sessions": [public_exercise_session(session) for session in sessions]}
    )


@router.post(
    "/check-ins",
    response_model=ApiEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_check_in(payload: CheckInCreateRequest, database: DatabaseDependency):
    if database.get_user(payload.user_id) is None:
        return failure(404, "not_found", "User was not found.")
    check_in = database.create_check_in(
        payload.user_id,
        payload.feeling,
        payload.color,
        payload.description,
        payload.check_in_date.isoformat(),
    )
    return success(public_check_in(check_in))


@router.get("/users/{user_id}/check-ins", response_model=ApiEnvelope)
def list_check_ins(user_id: int, database: DatabaseDependency):
    if database.get_user(user_id) is None:
        return failure(404, "not_found", "User was not found.")
    check_ins = database.list_check_ins(user_id)
    return success(
        {"check_ins": [public_check_in(check_in) for check_in in check_ins]}
    )


@router.patch("/check-ins/{check_in_id}", response_model=ApiEnvelope)
def update_check_in(
    check_in_id: int,
    payload: CheckInUpdateRequest,
    database: DatabaseDependency,
):
    check_in = database.update_check_in(
        check_in_id,
        feeling=payload.feeling,
        color=payload.color,
        description=payload.description,
    )
    if check_in is None:
        return failure(404, "not_found", "Check-in was not found.")
    return success(public_check_in(check_in))


@router.post("/chat/messages", response_model=ApiEnvelope)
def post_chat_message(
    payload: ChatMessageRequest,
    chat_service: ChatServiceDependency,
):
    try:
        result = chat_service.send_message(
            payload.user_id,
            payload.content,
            payload.conversation_id,
        )
    except ChatResourceNotFoundError:
        return failure(404, "not_found", "User or conversation was not found.")
    except ModelTimeoutError:
        return failure(504, "model_timeout", "The chat response timed out. Try again.")
    except ModelUnavailableError:
        return failure(
            503,
            "model_unavailable",
            "The chat response is temporarily unavailable. Try again.",
        )

    return success(
        {
            "conversation_id": result.conversation_id,
            "user_message": public_chat_message(result.user_message),
            "assistant_message": public_chat_message(result.assistant_message),
            "chat_mode": result.chat_mode,
        }
    )


@router.get("/users/{user_id}/conversations", response_model=ApiEnvelope)
def list_conversations(user_id: int, database: DatabaseDependency):
    if database.get_user(user_id) is None:
        return failure(404, "not_found", "User was not found.")
    conversations = reversed(database.list_conversations(user_id))
    return success(
        {
            "conversations": [
                public_conversation(conversation)
                for conversation in conversations
            ]
        }
    )


@router.get("/conversations/{conversation_id}/messages", response_model=ApiEnvelope)
def list_conversation_messages(
    conversation_id: int,
    database: DatabaseDependency,
):
    if database.get_conversation(conversation_id) is None:
        return failure(404, "not_found", "Conversation was not found.")
    messages = database.list_conversation_chat_logs(conversation_id)
    return success(
        {"messages": [public_chat_message(message) for message in messages]}
    )

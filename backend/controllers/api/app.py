"""Cornerstone FastAPI application factory and local entry point."""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from backend.controllers.database_controller import (
    DEFAULT_DATABASE_PATH,
    DatabaseController,
)
from backend.controllers.services import (
    AccountService,
    ChatProvider,
    ChatService,
    ProviderSettings,
    VoiceService,
    VoiceSettings,
    build_chat_provider,
)

from .responses import failure
from .routes import router


def create_app(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    *,
    chat_provider: ChatProvider | None = None,
    provider_settings: ProviderSettings | None = None,
    voice_service: VoiceService | None = None,
    voice_settings: VoiceSettings | None = None,
) -> FastAPI:
    database = DatabaseController(database_path)
    settings = provider_settings or ProviderSettings.from_environment()
    provider = chat_provider or build_chat_provider(settings)
    chat_service = ChatService(database, provider)
    account_service = AccountService(database)
    live_voice_service = voice_service or VoiceService(
        voice_settings or VoiceSettings.from_environment()
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database.initialize_schema()
        application.state.database_controller = database
        application.state.account_service = account_service
        application.state.chat_service = chat_service
        application.state.voice_service = live_voice_service
        yield

    application = FastAPI(
        title="Cornerstone API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.database_controller = database
    application.state.account_service = account_service
    application.state.chat_service = chat_service
    application.state.voice_service = live_voice_service
    application.include_router(router)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ):
        del request, error
        return failure(422, "validation_error", "Request input is invalid.")

    @application.exception_handler(sqlite3.IntegrityError)
    async def integrity_error_handler(request: Request, error: sqlite3.IntegrityError):
        del request, error
        return failure(409, "conflict", "Stored data conflicts with this request.")

    @application.exception_handler(sqlite3.DatabaseError)
    async def database_error_handler(request: Request, error: sqlite3.DatabaseError):
        del request, error
        return failure(500, "database_error", "Persistence is temporarily unavailable.")

    return application


app = create_app()

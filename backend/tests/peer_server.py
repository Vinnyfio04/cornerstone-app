"""Credential-free fictional peer fixture; never used by the production app."""

from pathlib import Path

from backend.controllers.api import create_app
from backend.controllers.services import ModelTimeoutError, ModelUnavailableError
from backend.controllers.services.voice_service import VoiceService, VoiceSettings


class PeerProvider:
    mode = "mock-peer"
    model_ready = True

    def generate(self, turns):
        content = turns[-1].content.strip()
        if content == "[test timeout]":
            raise ModelTimeoutError("Fictional peer timeout")
        if content == "[test unavailable]":
            raise ModelUnavailableError("Fictional peer failure")
        return (
            "Mocked response for fictional software testing. "
            "This checks chat delivery and saved history, not model quality."
        )


def create_peer_app(database_path: Path | None = None):
    return create_app(
        database_path
        if database_path is not None
        else Path(__file__).resolve().parents[1] / ".pytest_cache" / "peer-session.db",
        chat_provider=PeerProvider(),
        voice_service=VoiceService(VoiceSettings()),
    )

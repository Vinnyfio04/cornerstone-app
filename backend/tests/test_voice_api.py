import json
from types import SimpleNamespace

import pytest
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.controllers.api import create_app
from backend.controllers.api.routes import create_voice_session, get_voice_config
from backend.controllers.api.schemas import VoiceSessionRequest
from backend.controllers.services import (
    ALLOWED_CLIENT_EVENTS,
    ALLOWED_SERVER_EVENTS,
    DELEGATED_BACKEND_INSTRUCTIONS,
    DEFAULT_VOICE_DURATION_SECONDS,
    LIVE_INSTRUCTIONS,
    LIVE_MODEL,
    LIVE_REQUEST_TIMEOUT_SECONDS,
    MAX_SDP_BYTES,
    VoiceService,
    VoiceSettings,
)


SDP_OFFER = (
    "v=0\r\n"
    "o=- 100 2 IN IP4 127.0.0.1\r\n"
    "s=-\r\n"
    "t=0 0\r\n"
    "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
)
SDP_ANSWER = (
    "v=0\r\n"
    "o=- 200 2 IN IP4 127.0.0.1\r\n"
    "s=-\r\n"
    "t=0 0\r\n"
    "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
)


class FakeClientFactory:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.client_arguments = None
        self.create_arguments = None

    def __call__(self, **kwargs):
        self.client_arguments = kwargs
        return SimpleNamespace(live=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.create_arguments = kwargs
        if self.error is not None:
            raise self.error
        return self.response


def provider_response(
    *, session_id="live_test_session", sdp=SDP_ANSWER, transport_type="webrtc"
):
    return SimpleNamespace(
        session=SimpleNamespace(id=session_id),
        transport=SimpleNamespace(type=transport_type, sdp=sdp),
    )


def response_body(response):
    if isinstance(response, JSONResponse):
        return json.loads(response.body)
    return response


def test_voice_routes_are_registered(tmp_path):
    application = create_app(tmp_path / "route-registration.db")
    registered = {
        (method.upper(), path)
        for path, operations in application.openapi()["paths"].items()
        for method in operations
    }

    assert ("GET", "/api/voice/config") in registered
    assert ("POST", "/api/voice/sessions") in registered


def test_config_reports_missing_configuration_without_secrets(tmp_path):
    settings = VoiceSettings.from_environment({})
    service = VoiceService(settings, client_factory=FakeClientFactory())

    response = get_voice_config(service)

    assert response == {
        "data": {
            "status": "unconfigured",
            "duration_seconds": DEFAULT_VOICE_DURATION_SECONDS,
        },
        "error": None,
    }
    serialized = json.dumps(response).lower()
    assert "api_key" not in serialized
    assert "model" not in serialized
    assert "provider" not in serialized


def test_config_reports_server_duration_when_configured(tmp_path):
    settings = VoiceSettings.from_environment(
        {
            "OPEN_AI_API_KEY": "server-only-test-key",
            "VOICE_BACKEND_MODEL": "server-owned-backend-model",
            "VOICE_MAX_SESSION_SECONDS": "420",
        }
    )

    service = VoiceService(settings, client_factory=FakeClientFactory())
    response = get_voice_config(service)

    assert response == {
        "data": {"status": "configured", "duration_seconds": 420},
        "error": None,
    }
    assert "server-only-test-key" not in json.dumps(response)


def test_voice_requires_server_owned_backend_model(tmp_path):
    settings = VoiceSettings.from_environment(
        {"OPEN_AI_API_KEY": "server-only-test-key"}
    )
    service = VoiceService(settings, client_factory=FakeClientFactory())

    assert get_voice_config(service) == {
        "data": {
            "status": "unconfigured",
            "duration_seconds": DEFAULT_VOICE_DURATION_SECONDS,
        },
        "error": None,
    }


@pytest.mark.parametrize(
    "sdp_offer",
    [
        "not-sdp",
        "v=0\r\no=- 1 2 IN IP4 127.0.0.1\r\n",
        "v=0\r\nm=audio 9 RTP/AVP 0\r\na=" + ("x" * MAX_SDP_BYTES),
    ],
    ids=["not-sdp", "missing-audio", "oversized"],
)
def test_invalid_or_oversized_sdp_is_rejected_before_provider(
    tmp_path, sdp_offer
):
    factory = FakeClientFactory(response=provider_response())

    with pytest.raises(ValidationError):
        VoiceSessionRequest.model_validate({"sdp_offer": sdp_offer})
    assert factory.client_arguments is None


def test_browser_supplied_voice_configuration_is_rejected(tmp_path):
    factory = FakeClientFactory(response=provider_response())

    with pytest.raises(ValidationError):
        VoiceSessionRequest.model_validate(
            {
                "sdp_offer": SDP_OFFER,
                "model": "browser-model",
                "prompt": "browser prompt",
                "provider_url": "https://browser.invalid",
                "tools": ["browser-tool"],
                "duration_seconds": 999,
            }
        )

    assert factory.client_arguments is None


def test_session_creation_uses_bounded_server_owned_contract(tmp_path):
    factory = FakeClientFactory(response=provider_response())
    settings = VoiceSettings(
        api_key="server-only-test-key",
        backend_model="server-owned-backend-model",
        duration_seconds=360,
    )
    service = VoiceService(settings, client_factory=factory)

    response = create_voice_session(
        VoiceSessionRequest(sdp_offer=SDP_OFFER),
        service,
    )

    assert response == {
        "data": {
            "session_id": "live_test_session",
            "sdp_answer": SDP_ANSWER,
            "duration_seconds": 360,
        },
        "error": None,
    }
    assert factory.client_arguments == {
        "api_key": "server-only-test-key",
        "timeout": LIVE_REQUEST_TIMEOUT_SECONDS,
        "max_retries": 0,
    }
    assert factory.create_arguments["transport"] == {
        "type": "webrtc",
        "sdp": SDP_OFFER,
    }
    session = factory.create_arguments["session"]
    assert session["model"] == LIVE_MODEL == "gpt-live-1"
    assert session["instructions"] == LIVE_INSTRUCTIONS
    assert session["store"] is False
    assert "input" not in session
    assert session["delegation"] == {
        "type": "responses",
        "responses": {
            "model": "server-owned-backend-model",
            "instructions": DELEGATED_BACKEND_INSTRUCTIONS,
            "tools": [],
            "tool_choice": "none",
            "parallel_tool_calls": False,
            "max_output_tokens": 256,
        },
    }
    assert session["client"]["data_channel"] == {
        "allowed_client_events": list(ALLOWED_CLIENT_EVENTS),
        "allowed_server_events": [dict(event) for event in ALLOWED_SERVER_EVENTS],
    }
    assert ALLOWED_SERVER_EVENTS == (
        {"type": "session.started"},
        {"type": "session.input_transcript.delta"},
        {"type": "session.output_transcript.delta"},
        {"type": "session.closed"},
        {"type": "error"},
    )
    assert set(response["data"]) == {
        "session_id",
        "sdp_answer",
        "duration_seconds",
    }


def test_live_and_backend_prompt_layers_are_separate_and_bounded():
    assert "Speak warmly, naturally, and briefly at an unhurried pace" in LIVE_INSTRUCTIONS
    assert "Ask one focused question at a time" in LIVE_INSTRUCTIONS
    assert "Backchannel policy" in LIVE_INSTRUCTIONS
    assert "Allow interruption" in LIVE_INSTRUCTIONS
    assert "Generate <|SpawnThinking|>" in LIVE_INSTRUCTIONS

    assert "self-report" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "Ask permission before suggesting an activity" in (
        DELEGATED_BACKEND_INSTRUCTIONS
    )
    assert "context is missing" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "Do not diagnose" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "therapy or treatment" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "give medical advice" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "imply human monitoring" in DELEGATED_BACKEND_INSTRUCTIONS
    assert "records or context the application did not supply" in (
        DELEGATED_BACKEND_INSTRUCTIONS
    )
    assert "independent crisis-support route" in DELEGATED_BACKEND_INSTRUCTIONS


def test_provider_failure_is_sanitized(tmp_path):
    factory = FakeClientFactory(error=RuntimeError("sensitive provider detail"))
    settings = VoiceSettings(
        api_key="server-only-test-key",
        backend_model="server-owned-backend-model",
    )
    service = VoiceService(settings, client_factory=factory)

    response = create_voice_session(
        VoiceSessionRequest(sdp_offer=SDP_OFFER),
        service,
    )

    assert response.status_code == 503
    assert response_body(response) == {
        "data": None,
        "error": {
            "code": "voice_unavailable",
            "message": "Voice is temporarily unavailable. Try again.",
        },
    }
    assert "sensitive provider detail" not in response.body.decode()


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(),
        provider_response(session_id="bad session id"),
        provider_response(sdp="not-sdp"),
        provider_response(transport_type="websocket"),
    ],
)
def test_malformed_provider_response_is_sanitized(tmp_path, response):
    factory = FakeClientFactory(response=response)
    settings = VoiceSettings(
        api_key="server-only-test-key",
        backend_model="server-owned-backend-model",
    )
    service = VoiceService(settings, client_factory=factory)

    result = create_voice_session(
        VoiceSessionRequest(sdp_offer=SDP_OFFER),
        service,
    )

    assert result.status_code == 503
    assert response_body(result)["error"] == {
        "code": "voice_unavailable",
        "message": "Voice is temporarily unavailable. Try again.",
    }


def test_session_creation_fails_closed_when_configuration_is_missing(tmp_path):
    factory = FakeClientFactory(response=provider_response())
    service = VoiceService(VoiceSettings.from_environment({}), client_factory=factory)

    response = create_voice_session(
        VoiceSessionRequest(sdp_offer=SDP_OFFER),
        service,
    )

    assert response.status_code == 503
    assert response_body(response)["error"]["code"] == "voice_unavailable"
    assert factory.client_arguments is None

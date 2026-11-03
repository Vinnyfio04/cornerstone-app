"""Verify the peer fixture at the documented controller boundary."""

import json

from backend.controllers.api.routes import (
    get_health, get_voice_config, list_conversation_messages,
    post_chat_message, register_account,
)
from backend.controllers.api.schemas import AccountRegistrationRequest, ChatMessageRequest
from backend.tests.peer_server import create_peer_app


def test_peer_fixture_success_failures_and_disabled_voice(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'must-not-be-used')
    monkeypatch.setenv('VOICE_BACKEND_MODEL', 'must-not-be-used')
    database_path = tmp_path / 'peer.db'
    application = create_peer_app(database_path)
    database = application.state.database_controller
    database.initialize_schema()
    account = register_account(
        AccountRegistrationRequest(
            username='fictional.peer', first_name='Fictional', last_name='Peer',
            password='fictional-only-password',
        ),
        application.state.account_service,
    )['data']
    service = application.state.chat_service
    assert get_health(service)['data']['chat_mode'] == 'mock-peer'
    assert get_voice_config(application.state.voice_service)['data']['status'] == 'unconfigured'
    result = post_chat_message(
        ChatMessageRequest(user_id=account['id'], content='A fictional stressful assignment.'),
        service,
    )['data']
    conversation_id = result['conversation_id']
    assert result['assistant_message']['content'].startswith('Mocked response')
    for content, status_code, error_code in (
        ('[test timeout]', 504, 'model_timeout'),
        ('[test unavailable]', 503, 'model_unavailable'),
    ):
        failure = post_chat_message(
            ChatMessageRequest(user_id=account['id'], conversation_id=conversation_id, content=content),
            service,
        )
        assert failure.status_code == status_code
        assert json.loads(failure.body)['error']['code'] == error_code
    messages = list_conversation_messages(conversation_id, database)['data']['messages']
    assert [row['delivery_status'] for row in messages] == [
        'delivered', 'delivered', 'delivered', 'fallback', 'delivered', 'fallback',
    ]
    restarted = create_peer_app(database_path)
    restarted_database = restarted.state.database_controller
    restarted_database.initialize_schema()
    assert list_conversation_messages(conversation_id, restarted_database)['data']['messages'] == messages

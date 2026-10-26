import sqlite3

import pytest

from backend.controllers import DatabaseController


@pytest.fixture
def database(tmp_path):
    controller = DatabaseController(tmp_path / "cornerstone-test.db")
    controller.initialize_schema()
    return controller


def test_crud_and_relationships(database):
    user = database.create_user("Fictional User", {"pace": "gentle"})
    login = database.create_login(user.id, "fictional-user", "test-hash-only")
    conversation = database.create_conversation(user.id)
    first = database.create_chat_log(
        user.id,
        "user",
        "A fictional check-in",
        conversation_id=conversation.id,
    )
    second = database.create_chat_log(
        user.id,
        "assistant",
        "A bounded acknowledgement",
        "fallback",
        conversation_id=conversation.id,
    )
    session = database.create_exercise_session(
        user.id, "paced_breathing", 60_000, last_step="inhale_cycle_1"
    )

    assert database.get_user(user.id) == user
    assert database.get_login_by_username("FICTIONAL-USER") == login
    assert database.get_conversation(conversation.id) == conversation
    assert database.list_conversations(user.id) == [conversation]
    assert database.list_chat_logs(user.id) == [first, second]
    assert database.list_conversation_chat_logs(conversation.id) == [first, second]
    assert database.list_exercise_sessions(user.id) == [session]
    assert database.check_references() == []

    updated_user = database.update_user(user.id, display_name="Updated Fictional User")
    updated_login = database.update_login(login.id, username="updated-user")
    updated_chat = database.update_chat_log(second.id, delivery_status="delivered")
    updated_conversation = database.update_conversation(conversation.id)
    updated_session = database.update_exercise_session(
        session.id,
        measured_active_duration_ms=18_420,
        last_step="inhale_cycle_2",
        status="exited",
    )

    assert updated_user.display_name == "Updated Fictional User"
    assert updated_login.username == "updated-user"
    assert updated_chat.delivery_status == "delivered"
    assert updated_conversation.id == conversation.id
    assert updated_session.status == "exited"
    assert updated_session.measured_active_duration_ms == 18_420
    assert updated_session.last_step == "inhale_cycle_2"
    assert updated_session.ended_at is not None
    assert database.update_exercise_session(session.id, status="exited") == updated_session
    with pytest.raises(ValueError):
        database.update_exercise_session(session.id, status="completed")

    assert database.delete_chat_log(first.id) is True
    assert database.delete_exercise_session(session.id) is True
    assert database.delete_conversation(conversation.id) is True
    assert database.delete_login(login.id) is True
    assert database.delete_user(user.id) is True
    assert database.get_user(user.id) is None


def test_foreign_keys_are_enforced_and_user_delete_cascades(database):
    with pytest.raises(sqlite3.IntegrityError):
        database.create_chat_log(999, "user", "No matching user")

    user = database.create_user("Cascade User")
    login = database.create_login(user.id, "cascade-user", "test-hash-only")
    conversation = database.create_conversation(user.id)
    chat = database.create_chat_log(
        user.id,
        "user",
        "Delete with the user",
        conversation_id=conversation.id,
    )
    session = database.create_exercise_session(user.id, "sensory_grounding")

    assert database.delete_user(user.id) is True
    assert database.get_login(login.id) is None
    assert database.get_conversation(conversation.id) is None
    assert database.get_chat_log(chat.id) is None
    assert database.get_exercise_session(session.id) is None
    assert database.check_references() == []


def test_conversation_ownership_and_delete_cascade(database):
    first_user = database.create_user("First User")
    second_user = database.create_user("Second User")
    conversation = database.create_conversation(first_user.id)
    chat = database.create_chat_log(
        first_user.id,
        "user",
        "Owned message",
        conversation_id=conversation.id,
    )

    with pytest.raises(sqlite3.IntegrityError):
        database.create_chat_log(
            second_user.id,
            "user",
            "Wrong conversation owner",
            conversation_id=conversation.id,
        )

    assert database.delete_conversation(conversation.id) is True
    assert database.get_chat_log(chat.id) is None
    assert database.check_references() == []


def test_exercise_validation_and_completion(database):
    user = database.create_user("Exercise User")

    with pytest.raises(ValueError):
        database.create_exercise_session(user.id, "paced_breathing", -1)
    with pytest.raises(sqlite3.IntegrityError):
        database.create_exercise_session(user.id, "unknown_skill")

    session = database.create_exercise_session(
        user.id, "sensory_grounding", last_step="see_5"
    )
    completed = database.update_exercise_session(
        session.id,
        status="completed",
        measured_active_duration_ms=42_231,
        last_step="taste_1",
    )

    assert completed.status == "completed"
    assert completed.measured_active_duration_ms == 42_231
    assert completed.last_step == "taste_1"
    assert completed.ended_at is not None
    with pytest.raises(ValueError):
        database.update_exercise_session(session.id, measured_active_duration_ms=-1)


def test_legacy_chat_logs_are_migrated_without_row_loss(tmp_path):
    database_path = tmp_path / "legacy-cornerstone.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT NOT NULL,
                preferences_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                delivery_status TEXT NOT NULL DEFAULT 'delivered',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX idx_chat_logs_user_order ON chat_logs(user_id, id);

            INSERT INTO users (id, display_name) VALUES (7, 'Legacy User');
            INSERT INTO chat_logs (
                id, user_id, role, content, delivery_status, created_at
            ) VALUES
                (11, 7, 'user', 'First preserved row', 'delivered', '2026-01-01 10:00:00'),
                (12, 7, 'assistant', 'Second preserved row', 'fallback', '2026-01-01 10:01:00');
            """
        )

    controller = DatabaseController(database_path)
    controller.initialize_schema()
    controller.initialize_schema()

    conversations = controller.list_conversations(7)
    chat_logs = controller.list_chat_logs(7)

    assert len(conversations) == 1
    assert [chat.id for chat in chat_logs] == [11, 12]
    assert [chat.content for chat in chat_logs] == [
        "First preserved row",
        "Second preserved row",
    ]
    assert [chat.delivery_status for chat in chat_logs] == ["delivered", "fallback"]
    assert [chat.created_at for chat in chat_logs] == [
        "2026-01-01 10:00:00",
        "2026-01-01 10:01:00",
    ]
    assert {chat.conversation_id for chat in chat_logs} == {conversations[0].id}

    with controller.connect() as connection:
        columns = {
            row["name"]: row for row in connection.execute("PRAGMA table_info(chat_logs)")
        }
        table_names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert columns["conversation_id"]["notnull"] == 1
    assert "chat_logs_legacy" not in table_names
    assert controller.check_references() == []

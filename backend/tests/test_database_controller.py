import sqlite3

import pytest

from backend.controllers import DatabaseController


@pytest.fixture
def database(tmp_path):
    controller = DatabaseController(tmp_path / "cornerstone-test.db")
    controller.initialize_schema()
    return controller


def test_crud_and_relationships(database):
    user = database.create_user("Fictional", "User", {"pace": "gentle"})
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

    updated_user = database.update_user(
        user.id, first_name="Updated", last_name="Fictional User"
    )
    updated_login = database.update_login(login.id, username="updated-user")
    updated_chat = database.update_chat_log(second.id, delivery_status="delivered")
    updated_conversation = database.update_conversation(conversation.id)
    updated_session = database.update_exercise_session(
        session.id,
        measured_active_duration_ms=18_420,
        last_step="inhale_cycle_2",
        status="exited",
    )

    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Fictional User"
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


def test_account_creation_is_atomic_and_login_can_be_found_by_user(database):
    user, login = database.create_account(
        "Account", "User", "account-user", "pbkdf2-test-hash"
    )

    assert login.user_id == user.id
    assert database.get_login_by_user_id(user.id) == login

    with pytest.raises(sqlite3.IntegrityError):
        database.create_account(
            "Duplicate", "User", "ACCOUNT-USER", "another-hash"
        )

    assert [(stored.first_name, stored.last_name) for stored in database.list_users()] == [
        ("Account", "User")
    ]


def test_foreign_keys_are_enforced_and_user_delete_cascades(database):
    with pytest.raises(sqlite3.IntegrityError):
        database.create_chat_log(999, "user", "No matching user")

    user = database.create_user("Cascade", "User")
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
    first_user = database.create_user("First", "User")
    second_user = database.create_user("Second", "User")
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
    user = database.create_user("Exercise", "User")

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


def test_check_in_persistence_month_filter_uniqueness_and_cascade(database):
    user = database.create_user("Calendar", "User")
    october = database.create_check_in(
        user.id,
        "happy",
        "#d2a13f",
        "Finished a difficult assignment.",
        "2026-10-28",
    )
    november = database.create_check_in(
        user.id,
        "stressed",
        "#b06d4d",
        "A busy start to the month.",
        "2026-11-01",
    )

    assert database.get_check_in(october.id) == october
    assert database.list_check_ins(
        user.id,
        start_date="2026-10-01",
        end_date="2026-10-31",
    ) == [october]
    assert database.list_check_ins(user.id) == [october, november]

    updated = database.update_check_in(
        october.id,
        feeling="hopeful",
        color="#496db2",
        description="The assignment is finished and I feel lighter.",
    )
    assert updated.feeling == "hopeful"
    assert updated.color == "#496db2"
    assert updated.description == "The assignment is finished and I feel lighter."
    assert updated.check_in_date == "2026-10-28"

    with pytest.raises(sqlite3.IntegrityError):
        database.create_check_in(
            user.id, "sad", "#6f91aa", "Duplicate day.", "2026-10-28"
        )
    with pytest.raises(sqlite3.IntegrityError):
        database.create_check_in(
            user.id, "sad", "#6f91aa", "Invalid date.", "not-a-date"
        )
    with pytest.raises(sqlite3.IntegrityError):
        database.create_check_in(
            user.id, "sad", "blue", "Invalid color.", "2026-10-29"
        )

    assert database.delete_user(user.id) is True
    assert database.get_check_in(october.id) is None
    assert database.check_references() == []


def test_existing_check_ins_receive_a_default_marker_color(tmp_path):
    database_path = tmp_path / "legacy-check-ins.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                preferences_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE check_ins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feeling TEXT NOT NULL,
                description TEXT NOT NULL,
                check_in_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, check_in_date)
            );
            INSERT INTO users (id, first_name, last_name) VALUES (1, 'Existing', 'User');
            INSERT INTO check_ins (
                id, user_id, feeling, description, check_in_date
            ) VALUES (1, 1, 'overwhelmed', 'Preserve this row.', '2026-10-27');
            """
        )

    controller = DatabaseController(database_path)
    controller.initialize_schema()

    restored = controller.get_check_in(1)
    assert restored.feeling == "overwhelmed"
    assert restored.color == "#66836e"
    assert restored.description == "Preserve this row."


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
    migrated_user = controller.get_user(7)

    assert len(conversations) == 1
    assert migrated_user.first_name == "Legacy"
    assert migrated_user.last_name == "User"
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
        user_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)")
        }
        table_names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert columns["conversation_id"]["notnull"] == 1
    assert "display_name" not in user_columns
    assert {"first_name", "last_name"} <= user_columns
    assert "chat_logs_legacy" not in table_names
    assert controller.check_references() == []

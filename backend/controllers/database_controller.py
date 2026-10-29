"""SQLite database controller for the MVC model layer."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from backend.models import CheckIn, ChatLog, Conversation, ExerciseSession, Login, User


DEFAULT_DATABASE_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "data" / "cornerstone.db"
)


class DatabaseController:
    """Open SQLite connections and perform CRUD for Cornerstone models."""

    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Open one transaction with foreign-key enforcement enabled."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_schema(self) -> None:
        """Create or migrate the model schema without discarding existing rows."""
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL CHECK (trim(first_name) <> ''),
                    last_name TEXT NOT NULL CHECK (trim(last_name) <> ''),
                    preferences_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS login (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL COLLATE NOCASE UNIQUE
                        CHECK (trim(username) <> ''),
                    password_hash TEXT NOT NULL CHECK (trim(password_hash) <> ''),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_user_order
                    ON conversations(user_id, id);

                CREATE TABLE IF NOT EXISTS exercise_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    skill TEXT NOT NULL
                        CHECK (skill IN ('paced_breathing', 'sensory_grounding')),
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'completed', 'exited')),
                    planned_duration_ms INTEGER
                        CHECK (planned_duration_ms IS NULL OR planned_duration_ms >= 0),
                    measured_active_duration_ms INTEGER NOT NULL DEFAULT 0
                        CHECK (measured_active_duration_ms >= 0),
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ended_at TEXT,
                    last_step TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_exercise_sessions_user_order
                    ON exercise_sessions(user_id, id);

                CREATE TABLE IF NOT EXISTS check_ins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    feeling TEXT NOT NULL CHECK (trim(feeling) <> ''),
                    color TEXT NOT NULL DEFAULT '#66836e'
                        CHECK (color GLOB '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'),
                    description TEXT NOT NULL CHECK (trim(description) <> ''),
                    check_in_date TEXT NOT NULL
                        CHECK (check_in_date IS date(check_in_date)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE (user_id, check_in_date)
                );

                CREATE INDEX IF NOT EXISTS idx_check_ins_user_date
                    ON check_ins(user_id, check_in_date);
                """
            )
            self._initialize_users_schema(connection)
            self._initialize_chat_logs_schema(connection)
            self._initialize_check_ins_schema(connection)
            if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise RuntimeError("SQLite foreign-key enforcement is disabled")

    @staticmethod
    def _initialize_users_schema(connection: sqlite3.Connection) -> None:
        """Migrate the former display label into explicit first/last name fields."""
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)")
        }
        if "display_name" in columns and "first_name" not in columns:
            connection.execute(
                "ALTER TABLE users RENAME COLUMN display_name TO first_name"
            )
            columns.remove("display_name")
            columns.add("first_name")
        if "last_name" not in columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN last_name TEXT NOT NULL DEFAULT ''"
            )
            connection.execute(
                """
                UPDATE users
                SET
                    last_name = substr(trim(first_name), instr(trim(first_name), ' ') + 1),
                    first_name = substr(trim(first_name), 1, instr(trim(first_name), ' ') - 1)
                WHERE instr(trim(first_name), ' ') > 0
                  AND trim(last_name) = ''
                """
            )

    @staticmethod
    def _initialize_chat_logs_schema(connection: sqlite3.Connection) -> None:
        existing_table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'chat_logs'"
        ).fetchone()

        if existing_table is None:
            DatabaseController._create_chat_logs_table(connection)
        else:
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(chat_logs)")
            }
            if "conversation_id" not in columns:
                DatabaseController._migrate_legacy_chat_logs(connection)

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_logs_user_order
            ON chat_logs(user_id, id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_logs_conversation_order
            ON chat_logs(conversation_id, id)
            """
        )

    @staticmethod
    def _initialize_check_ins_schema(connection: sqlite3.Connection) -> None:
        """Add marker color without discarding check-ins from an older schema."""
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(check_ins)")
        }
        if "color" not in columns:
            connection.execute(
                """
                ALTER TABLE check_ins
                ADD COLUMN color TEXT NOT NULL DEFAULT '#66836e'
                """
            )

    @staticmethod
    def _create_chat_logs_table(
        connection: sqlite3.Connection, table_name: str = "chat_logs"
    ) -> None:
        if table_name not in {"chat_logs", "chat_logs_current"}:
            raise ValueError("Unexpected chat-log migration table name")

        connection.execute(
            f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL CHECK (trim(content) <> ''),
                delivery_status TEXT NOT NULL DEFAULT 'delivered'
                    CHECK (delivery_status IN ('delivered', 'fallback', 'failed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
            """
        )

    @staticmethod
    def _migrate_legacy_chat_logs(connection: sqlite3.Connection) -> None:
        """Group legacy user messages into one preserved conversation per user."""
        connection.execute("SAVEPOINT migrate_legacy_chat_logs")
        try:
            legacy_rows = connection.execute(
                "SELECT * FROM chat_logs ORDER BY id"
            ).fetchall()
            conversation_ids: dict[int, int] = {}

            for row in legacy_rows:
                user_id = row["user_id"]
                if user_id in conversation_ids:
                    continue
                user_timestamps = [
                    item["created_at"]
                    for item in legacy_rows
                    if item["user_id"] == user_id
                ]
                cursor = connection.execute(
                    """
                    INSERT INTO conversations (user_id, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, min(user_timestamps), max(user_timestamps)),
                )
                conversation_ids[user_id] = int(cursor.lastrowid)

            connection.execute("ALTER TABLE chat_logs RENAME TO chat_logs_legacy")
            DatabaseController._create_chat_logs_table(connection, "chat_logs_current")

            connection.executemany(
                """
                INSERT INTO chat_logs_current (
                    id, user_id, conversation_id, role, content,
                    delivery_status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row["id"],
                        row["user_id"],
                        conversation_ids[row["user_id"]],
                        row["role"],
                        row["content"],
                        row["delivery_status"],
                        row["created_at"],
                    )
                    for row in legacy_rows
                ],
            )
            connection.execute("DROP TABLE chat_logs_legacy")
            connection.execute("ALTER TABLE chat_logs_current RENAME TO chat_logs")
        except Exception:
            connection.execute("ROLLBACK TO SAVEPOINT migrate_legacy_chat_logs")
            connection.execute("RELEASE SAVEPOINT migrate_legacy_chat_logs")
            raise
        else:
            connection.execute("RELEASE SAVEPOINT migrate_legacy_chat_logs")

    def check_references(self) -> list[dict[str, Any]]:
        """Return all foreign-key violations reported by SQLite."""
        with self.connect() as connection:
            rows = connection.execute("PRAGMA foreign_key_check").fetchall()
        return [dict(row) for row in rows]

    def create_user(
        self,
        first_name: str,
        last_name: str,
        preferences: dict[str, Any] | None = None,
    ) -> User:
        preferences_json = json.dumps(preferences or {}, sort_keys=True)
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO users (first_name, last_name, preferences_json) VALUES (?, ?, ?)",
                (first_name, last_name, preferences_json),
            )
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._user(row)

    def create_account(
        self,
        first_name: str,
        last_name: str,
        username: str,
        password_hash: str,
        preferences: dict[str, Any] | None = None,
    ) -> tuple[User, Login]:
        """Create a user and login together so a failed credential insert leaves no orphan."""
        preferences_json = json.dumps(preferences or {}, sort_keys=True)
        with self.connect() as connection:
            user_cursor = connection.execute(
                "INSERT INTO users (first_name, last_name, preferences_json) VALUES (?, ?, ?)",
                (first_name, last_name, preferences_json),
            )
            user_id = int(user_cursor.lastrowid)
            login_cursor = connection.execute(
                "INSERT INTO login (user_id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, password_hash),
            )
            user_row = connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            login_row = connection.execute(
                "SELECT * FROM login WHERE id = ?", (login_cursor.lastrowid,)
            ).fetchone()
        return self._user(user_row), self._login(login_row)

    def get_user(self, user_id: int) -> User | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._user(row) if row else None

    def list_users(self) -> list[User]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [self._user(row) for row in rows]

    def update_user(
        self,
        user_id: int,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> User | None:
        assignments: list[str] = []
        values: list[Any] = []
        if first_name is not None:
            assignments.append("first_name = ?")
            values.append(first_name)
        if last_name is not None:
            assignments.append("last_name = ?")
            values.append(last_name)
        if preferences is not None:
            assignments.append("preferences_json = ?")
            values.append(json.dumps(preferences, sort_keys=True))
        if not assignments:
            return self.get_user(user_id)
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE users SET {', '.join(assignments)} WHERE id = ?", values
            )
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._user(row) if row else None

    def delete_user(self, user_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount == 1

    def create_conversation(self, user_id: int) -> Conversation:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO conversations (user_id) VALUES (?)", (user_id,)
            )
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._conversation(row)

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
        return self._conversation(row) if row else None

    def list_conversations(self, user_id: int) -> list[Conversation]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM conversations WHERE user_id = ? ORDER BY id",
                (user_id,),
            ).fetchall()
        return [self._conversation(row) for row in rows]

    def update_conversation(self, conversation_id: int) -> Conversation | None:
        """Touch a conversation after message activity."""
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (conversation_id,),
            )
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
        return self._conversation(row) if row else None

    def delete_conversation(self, conversation_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM conversations WHERE id = ?", (conversation_id,)
            )
        return cursor.rowcount == 1

    def create_login(self, user_id: int, username: str, password_hash: str) -> Login:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO login (user_id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, password_hash),
            )
            row = connection.execute(
                "SELECT * FROM login WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._login(row)

    def get_login(self, login_id: int) -> Login | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM login WHERE id = ?", (login_id,)
            ).fetchone()
        return self._login(row) if row else None

    def get_login_by_username(self, username: str) -> Login | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM login WHERE username = ?", (username,)
            ).fetchone()
        return self._login(row) if row else None

    def get_login_by_user_id(self, user_id: int) -> Login | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM login WHERE user_id = ?", (user_id,)
            ).fetchone()
        return self._login(row) if row else None

    def update_login(
        self,
        login_id: int,
        *,
        username: str | None = None,
        password_hash: str | None = None,
    ) -> Login | None:
        assignments: list[str] = []
        values: list[Any] = []
        if username is not None:
            assignments.append("username = ?")
            values.append(username)
        if password_hash is not None:
            assignments.append("password_hash = ?")
            values.append(password_hash)
        if not assignments:
            return self.get_login(login_id)
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        values.append(login_id)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE login SET {', '.join(assignments)} WHERE id = ?", values
            )
            row = connection.execute(
                "SELECT * FROM login WHERE id = ?", (login_id,)
            ).fetchone()
        return self._login(row) if row else None

    def delete_login(self, login_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM login WHERE id = ?", (login_id,))
        return cursor.rowcount == 1

    def create_chat_log(
        self,
        user_id: int,
        role: str,
        content: str,
        delivery_status: str = "delivered",
        *,
        conversation_id: int | None = None,
    ) -> ChatLog:
        with self.connect() as connection:
            if conversation_id is None:
                conversation_cursor = connection.execute(
                    "INSERT INTO conversations (user_id) VALUES (?)", (user_id,)
                )
                conversation_id = int(conversation_cursor.lastrowid)
            elif (
                connection.execute(
                    """
                    SELECT 1 FROM conversations
                    WHERE id = ? AND user_id = ?
                    """,
                    (conversation_id, user_id),
                ).fetchone()
                is None
            ):
                raise sqlite3.IntegrityError(
                    "Conversation does not exist for the specified user"
                )

            cursor = connection.execute(
                """
                INSERT INTO chat_logs (
                    user_id, conversation_id, role, content, delivery_status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, conversation_id, role, content, delivery_status),
            )
            connection.execute(
                """
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (conversation_id,),
            )
            row = connection.execute(
                "SELECT * FROM chat_logs WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._chat_log(row)

    def get_chat_log(self, chat_log_id: int) -> ChatLog | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM chat_logs WHERE id = ?", (chat_log_id,)
            ).fetchone()
        return self._chat_log(row) if row else None

    def list_chat_logs(self, user_id: int) -> list[ChatLog]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM chat_logs WHERE user_id = ? ORDER BY id", (user_id,)
            ).fetchall()
        return [self._chat_log(row) for row in rows]

    def list_conversation_chat_logs(self, conversation_id: int) -> list[ChatLog]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chat_logs
                WHERE conversation_id = ?
                ORDER BY id
                """,
                (conversation_id,),
            ).fetchall()
        return [self._chat_log(row) for row in rows]

    def update_chat_log(
        self,
        chat_log_id: int,
        *,
        content: str | None = None,
        delivery_status: str | None = None,
    ) -> ChatLog | None:
        assignments: list[str] = []
        values: list[Any] = []
        if content is not None:
            assignments.append("content = ?")
            values.append(content)
        if delivery_status is not None:
            assignments.append("delivery_status = ?")
            values.append(delivery_status)
        if not assignments:
            return self.get_chat_log(chat_log_id)
        values.append(chat_log_id)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE chat_logs SET {', '.join(assignments)} WHERE id = ?", values
            )
            row = connection.execute(
                "SELECT * FROM chat_logs WHERE id = ?", (chat_log_id,)
            ).fetchone()
            if row:
                connection.execute(
                    """
                    UPDATE conversations
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (row["conversation_id"],),
                )
        return self._chat_log(row) if row else None

    def delete_chat_log(self, chat_log_id: int) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT conversation_id FROM chat_logs WHERE id = ?", (chat_log_id,)
            ).fetchone()
            cursor = connection.execute(
                "DELETE FROM chat_logs WHERE id = ?", (chat_log_id,)
            )
            if row:
                connection.execute(
                    """
                    UPDATE conversations
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (row["conversation_id"],),
                )
        return cursor.rowcount == 1

    def create_exercise_session(
        self,
        user_id: int,
        skill: str,
        planned_duration_ms: int | None = None,
        *,
        last_step: str | None = None,
    ) -> ExerciseSession:
        if planned_duration_ms is not None and planned_duration_ms < 0:
            raise ValueError("Planned duration cannot be negative")

        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO exercise_sessions (
                    user_id, skill, planned_duration_ms, last_step
                )
                VALUES (?, ?, ?, ?)
                """,
                (user_id, skill, planned_duration_ms, last_step),
            )
            row = connection.execute(
                "SELECT * FROM exercise_sessions WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._exercise_session(row)

    def get_exercise_session(self, session_id: int) -> ExerciseSession | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM exercise_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return self._exercise_session(row) if row else None

    def list_exercise_sessions(self, user_id: int) -> list[ExerciseSession]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM exercise_sessions
                WHERE user_id = ?
                ORDER BY id
                """,
                (user_id,),
            ).fetchall()
        return [self._exercise_session(row) for row in rows]

    def update_exercise_session(
        self,
        session_id: int,
        *,
        status: str | None = None,
        measured_active_duration_ms: int | None = None,
        last_step: str | None = None,
    ) -> ExerciseSession | None:
        if status is not None and status not in {"completed", "exited"}:
            raise ValueError("Exercise status must be completed or exited")
        if (
            measured_active_duration_ms is not None
            and measured_active_duration_ms < 0
        ):
            raise ValueError("Measured duration cannot be negative")

        current = self.get_exercise_session(session_id)
        if current is None:
            return None
        if current.status != "active":
            if status == current.status:
                return current
            raise ValueError("A terminal exercise session cannot be changed")

        assignments: list[str] = []
        values: list[Any] = []
        if measured_active_duration_ms is not None:
            assignments.append("measured_active_duration_ms = ?")
            values.append(measured_active_duration_ms)
        if last_step is not None:
            assignments.append("last_step = ?")
            values.append(last_step)
        if status is not None:
            assignments.extend(["status = ?", "ended_at = CURRENT_TIMESTAMP"])
            values.append(status)
        if not assignments:
            return current

        values.append(session_id)
        with self.connect() as connection:
            connection.execute(
                f"""
                UPDATE exercise_sessions
                SET {', '.join(assignments)}
                WHERE id = ?
                """,
                values,
            )
            row = connection.execute(
                "SELECT * FROM exercise_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return self._exercise_session(row)

    def delete_exercise_session(self, session_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM exercise_sessions WHERE id = ?", (session_id,)
            )
        return cursor.rowcount == 1

    def create_check_in(
        self,
        user_id: int,
        feeling: str,
        color: str,
        description: str,
        check_in_date: str,
    ) -> CheckIn:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO check_ins (
                    user_id, feeling, color, description, check_in_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, feeling, color, description, check_in_date),
            )
            row = connection.execute(
                "SELECT * FROM check_ins WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._check_in(row)

    def get_check_in(self, check_in_id: int) -> CheckIn | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM check_ins WHERE id = ?", (check_in_id,)
            ).fetchone()
        return self._check_in(row) if row else None

    def list_check_ins(
        self,
        user_id: int,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[CheckIn]:
        conditions = ["user_id = ?"]
        values: list[Any] = [user_id]
        if start_date is not None:
            conditions.append("check_in_date >= ?")
            values.append(start_date)
        if end_date is not None:
            conditions.append("check_in_date <= ?")
            values.append(end_date)
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM check_ins
                WHERE {' AND '.join(conditions)}
                ORDER BY check_in_date, id
                """,
                values,
            ).fetchall()
        return [self._check_in(row) for row in rows]

    def update_check_in(
        self,
        check_in_id: int,
        *,
        feeling: str | None = None,
        color: str | None = None,
        description: str | None = None,
    ) -> CheckIn | None:
        assignments: list[str] = []
        values: list[Any] = []
        if feeling is not None:
            assignments.append("feeling = ?")
            values.append(feeling)
        if color is not None:
            assignments.append("color = ?")
            values.append(color)
        if description is not None:
            assignments.append("description = ?")
            values.append(description)
        if not assignments:
            return self.get_check_in(check_in_id)

        values.append(check_in_id)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE check_ins SET {', '.join(assignments)} WHERE id = ?",
                values,
            )
            row = connection.execute(
                "SELECT * FROM check_ins WHERE id = ?", (check_in_id,)
            ).fetchone()
        return self._check_in(row) if row else None

    def delete_check_in(self, check_in_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM check_ins WHERE id = ?", (check_in_id,)
            )
        return cursor.rowcount == 1

    @staticmethod
    def _user(row: sqlite3.Row) -> User:
        return User(**dict(row))

    @staticmethod
    def _login(row: sqlite3.Row) -> Login:
        return Login(**dict(row))

    @staticmethod
    def _chat_log(row: sqlite3.Row) -> ChatLog:
        return ChatLog(**dict(row))

    @staticmethod
    def _conversation(row: sqlite3.Row) -> Conversation:
        return Conversation(**dict(row))

    @staticmethod
    def _exercise_session(row: sqlite3.Row) -> ExerciseSession:
        return ExerciseSession(**dict(row))

    @staticmethod
    def _check_in(row: sqlite3.Row) -> CheckIn:
        return CheckIn(**dict(row))

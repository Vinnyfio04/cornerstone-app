"""Account creation and credential verification for the local prototype."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

from backend.controllers.database_controller import DatabaseController
from backend.models import User


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000
SALT_BYTES = 16


class InvalidCredentialsError(Exception):
    """Raised when a username/password pair cannot be verified."""


class AccountNotFoundError(Exception):
    """Raised when a user does not have an active login record."""


@dataclass(frozen=True)
class AccountResult:
    user: User
    username: str


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return "$".join(
        (
            PASSWORD_SCHEME,
            str(PASSWORD_ITERATIONS),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        scheme, iterations_text, salt_text, digest_text = encoded_hash.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected_digest = base64.urlsafe_b64decode(digest_text.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual_digest, expected_digest)


class AccountService:
    def __init__(self, database: DatabaseController) -> None:
        self.database = database

    def register(
        self,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> AccountResult:
        user, login = self.database.create_account(
            first_name,
            last_name,
            username,
            hash_password(password),
        )
        return AccountResult(user=user, username=login.username)

    def login(self, username: str, password: str) -> AccountResult:
        login = self.database.get_login_by_username(username)
        if login is None or not verify_password(password, login.password_hash):
            raise InvalidCredentialsError
        user = self.database.get_user(login.user_id)
        if user is None:
            raise InvalidCredentialsError
        return AccountResult(user=user, username=login.username)

    def get(self, user_id: int) -> AccountResult:
        user = self.database.get_user(user_id)
        login = self.database.get_login_by_user_id(user_id)
        if user is None or login is None:
            raise AccountNotFoundError
        return AccountResult(user=user, username=login.username)

    def update(
        self,
        user_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        password: str | None = None,
    ) -> AccountResult:
        self.get(user_id)
        login = self.database.get_login_by_user_id(user_id)
        if username is not None or password is not None:
            login = self.database.update_login(
                login.id,
                username=username,
                password_hash=hash_password(password) if password is not None else None,
            )
        user = self.database.update_user(
            user_id,
            first_name=first_name,
            last_name=last_name,
        )
        if user is None or login is None:
            raise AccountNotFoundError
        return AccountResult(user=user, username=login.username)

    def delete(self, user_id: int) -> bool:
        self.get(user_id)
        return self.database.delete_user(user_id)

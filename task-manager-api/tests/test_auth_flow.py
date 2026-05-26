"""Integration-style tests for the auth flow.

Uses the real FastAPI application with TestClient, overriding dependencies
to avoid needing a real PostgreSQL instance.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.presentation.api.v1.dependencies import (
    get_user_repo,
    get_password_service,
    get_jwt_service,
)


def _make_user_mock(
    user_id: int = 1,
    email: str = "test@example.com",
    full_name: str = "Test User",
    hashed_pwd: str = "hashed_secret123",
):
    """Helper to create a mock user that behaves like a domain User entity."""
    user = AsyncMock()
    user.id = user_id
    user.email = email
    user.full_name = full_name
    user.hashed_password = hashed_pwd
    return user


def _make_pwd_mock():
    """Create a password service mock with simple string-based hashing."""
    pwd = AsyncMock()
    pwd.hash_password = lambda p: f"hashed_{p}"
    pwd.verify_password = lambda p, h: h == f"hashed_{p}"
    return pwd


def _make_jwt_mock():
    """Create a JWT service mock that returns a predictable token."""
    jwt = AsyncMock()
    jwt.create_access_token = lambda data, expires_delta=None: "mocked_token_" + data.get("sub", "unknown")
    jwt.decode_access_token = lambda token: {"sub": "1", "email": "test@example.com"}
    return jwt


def _override(overrides: dict) -> None:
    """Apply dependency overrides to the app."""
    app.dependency_overrides.update(overrides)


def _clear_overrides() -> None:
    """Remove all dependency overrides from the app."""
    app.dependency_overrides.clear()


client = TestClient(app)


def test_register_and_login_flow() -> None:
    """Register a user, then login with the same credentials."""
    created_user = _make_user_mock(user_id=1, email="new@example.com", full_name="New User")

    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = None
    user_repo.create.return_value = created_user

    _override({
        get_user_repo: lambda: user_repo,
        get_password_service: _make_pwd_mock,
        get_jwt_service: _make_jwt_mock,
    })

    try:
        # ── Register ──
        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "secret123", "full_name": "New User"},
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["user"]["email"] == "new@example.com"
        assert "access_token" in register_data

        # ── Login ──
        user_repo.get_by_email.return_value = created_user

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "new@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["access_token"] is not None
        assert login_data["user"]["email"] == "new@example.com"
    finally:
        _clear_overrides()


def test_register_duplicate_email_returns_409() -> None:
    """Registering with an existing email returns 409."""
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = _make_user_mock(email="existing@example.com")

    _override({
        get_user_repo: lambda: user_repo,
        get_password_service: _make_pwd_mock,
        get_jwt_service: _make_jwt_mock,
    })

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "existing@example.com", "password": "secret123", "full_name": "Existing"},
        )
        assert response.status_code == 409
        assert response.json()["code"] == "DUPLICATE_EMAIL"
    finally:
        _clear_overrides()


def test_login_invalid_credentials_returns_401() -> None:
    """Login with wrong email returns 401."""
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = None

    _override({
        get_user_repo: lambda: user_repo,
        get_password_service: _make_pwd_mock,
        get_jwt_service: _make_jwt_mock,
    })

    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrong"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"
    finally:
        _clear_overrides()


def test_login_wrong_password_returns_401() -> None:
    """Login with wrong password returns 401."""
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = _make_user_mock(
        email="test@example.com", hashed_pwd="hashed_correct_password"
    )

    _override({
        get_user_repo: lambda: user_repo,
        get_password_service: _make_pwd_mock,
        get_jwt_service: _make_jwt_mock,
    })

    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"
    finally:
        _clear_overrides()

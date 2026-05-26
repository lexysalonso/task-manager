"""RegisterUserUseCase tests with mocked repository."""

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.application.dtos.auth_dtos import RegisterInput
from src.domain.exceptions import DuplicateEmailError


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = None
    user_repo.create.return_value = AsyncMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
    )

    pwd_service = AsyncMock()
    pwd_service.hash_password.return_value = "hashed_pwd"

    use_case = RegisterUserUseCase(user_repo, pwd_service)
    result = await use_case.execute(
        RegisterInput(email="test@example.com", password="secret123", full_name="Test User")
    )

    assert result.id == 1
    assert result.email == "test@example.com"
    user_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    user_repo = AsyncMock()
    user_repo.get_by_email.return_value = AsyncMock(id=1, email="existing@example.com")

    pwd_service = AsyncMock()

    use_case = RegisterUserUseCase(user_repo, pwd_service)
    with pytest.raises(DuplicateEmailError):
        await use_case.execute(
            RegisterInput(email="existing@example.com", password="secret123", full_name="Existing")
        )
    user_repo.create.assert_not_awaited()

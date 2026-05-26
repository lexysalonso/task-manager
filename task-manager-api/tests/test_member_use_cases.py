"""Member use case tests with mocked repositories."""

from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.application.use_cases.projects.add_member import AddMemberUseCase
from src.application.use_cases.projects.list_members import ListMembersUseCase
from src.application.use_cases.projects.remove_member import RemoveMemberUseCase
from src.application.use_cases.users.search_users import SearchUsersUseCase
from src.domain.entities.project import Project, ProjectMember
from src.domain.entities.user import User
from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectOwnerError,
    NotProjectMemberError,
    UserNotFoundError,
    CannotRemoveOwnerError,
)


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id=1, name="Test Project", description="",
        is_archived=False, owner_id=1,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Project(**defaults)


# ── Add Member ─────────────────────────────────────


@pytest.mark.asyncio
async def test_add_member_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = False

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = User(id=2, email="user2@test.com", full_name="User 2")

    use_case = AddMemberUseCase(project_repo, user_repo)
    await use_case.execute(project_id=1, target_user_id=2, current_user_id=1)

    project_repo.add_member.assert_awaited_once_with(1, 2)


@pytest.mark.asyncio
async def test_add_member_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = AddMemberUseCase(project_repo, AsyncMock())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, target_user_id=2, current_user_id=1)


@pytest.mark.asyncio
async def test_add_member_not_owner() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)

    use_case = AddMemberUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectOwnerError):
        await use_case.execute(project_id=1, target_user_id=2, current_user_id=3)


@pytest.mark.asyncio
async def test_add_member_user_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = False

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = None

    use_case = AddMemberUseCase(project_repo, user_repo)
    with pytest.raises(UserNotFoundError):
        await use_case.execute(project_id=1, target_user_id=999, current_user_id=1)


@pytest.mark.asyncio
async def test_add_member_already_member_returns_silently() -> None:
    """Adding a user who is already a member should silently succeed (idempotent)."""
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True  # already a member

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = User(id=2, email="user2@test.com")

    use_case = AddMemberUseCase(project_repo, user_repo)
    await use_case.execute(project_id=1, target_user_id=2, current_user_id=1)

    project_repo.add_member.assert_not_awaited()


# ── List Members ───────────────────────────────────


@pytest.mark.asyncio
async def test_list_members_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.get_members.return_value = [
        ProjectMember(project_id=1, user_id=1, user_email="owner@test.com", full_name="Owner"),
        ProjectMember(project_id=1, user_id=2, user_email="member@test.com", full_name="Member"),
    ]

    use_case = ListMembersUseCase(project_repo)
    result = await use_case.execute(project_id=1, user_id=1)

    assert len(result) == 2
    assert result[0].user_id == 1
    assert result[1].email == "member@test.com"


@pytest.mark.asyncio
async def test_list_members_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = ListMembersUseCase(project_repo)
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, user_id=1)


@pytest.mark.asyncio
async def test_list_members_not_member() -> None:
    """Non-members cannot list members (unless they are the owner)."""
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = False

    use_case = ListMembersUseCase(project_repo)
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(project_id=1, user_id=3)


# ── Remove Member ──────────────────────────────────


@pytest.mark.asyncio
async def test_remove_member_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = User(id=2, email="user2@test.com")

    task_repo = AsyncMock()

    use_case = RemoveMemberUseCase(project_repo, user_repo, task_repo)
    await use_case.execute(project_id=1, target_user_id=2, current_user_id=1)

    task_repo.reassign_by_user.assert_awaited_once_with(1, 2, 1)
    project_repo.remove_member.assert_awaited_once_with(1, 2)


@pytest.mark.asyncio
async def test_remove_member_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = RemoveMemberUseCase(project_repo, AsyncMock(), AsyncMock())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, target_user_id=2, current_user_id=1)


@pytest.mark.asyncio
async def test_remove_member_not_owner() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)

    use_case = RemoveMemberUseCase(project_repo, AsyncMock(), AsyncMock())
    with pytest.raises(NotProjectOwnerError):
        await use_case.execute(project_id=1, target_user_id=2, current_user_id=3)


@pytest.mark.asyncio
async def test_remove_member_cannot_remove_owner() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)

    use_case = RemoveMemberUseCase(project_repo, AsyncMock(), AsyncMock())
    with pytest.raises(CannotRemoveOwnerError):
        await use_case.execute(project_id=1, target_user_id=1, current_user_id=1)


@pytest.mark.asyncio
async def test_remove_member_user_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = None

    use_case = RemoveMemberUseCase(project_repo, user_repo, AsyncMock())
    with pytest.raises(UserNotFoundError):
        await use_case.execute(project_id=1, target_user_id=999, current_user_id=1)


@pytest.mark.asyncio
async def test_remove_member_not_a_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = False

    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = User(id=3, email="user3@test.com")

    use_case = RemoveMemberUseCase(project_repo, user_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(project_id=1, target_user_id=3, current_user_id=1)


# ── Search Users ───────────────────────────────────


@pytest.mark.asyncio
async def test_search_users_success() -> None:
    user_repo = AsyncMock()
    user_repo.search.return_value = [
        User(id=1, email="alice@test.com", full_name="Alice"),
        User(id=2, email="bob@test.com", full_name="Bob"),
    ]

    use_case = SearchUsersUseCase(user_repo)
    result = await use_case.execute(query="alice")

    assert len(result) == 2
    assert result[0].email == "alice@test.com"


@pytest.mark.asyncio
async def test_search_users_empty_query() -> None:
    user_repo = AsyncMock()
    user_repo.search.return_value = []

    use_case = SearchUsersUseCase(user_repo)
    result = await use_case.execute(query="")

    assert len(result) == 0

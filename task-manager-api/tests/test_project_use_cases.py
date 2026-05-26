"""Project use case tests with mocked repositories."""

from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.application.use_cases.projects.create_project import CreateProjectUseCase
from src.application.use_cases.projects.get_project import GetProjectUseCase
from src.application.use_cases.projects.list_projects import ListProjectsUseCase
from src.application.use_cases.projects.update_project import UpdateProjectUseCase
from src.application.use_cases.projects.delete_project import DeleteProjectUseCase
from src.application.dtos.project_dtos import CreateProjectInput, UpdateProjectInput
from src.domain.entities.project import Project, ProjectMember
from src.domain.exceptions import ProjectNotFoundError, NotProjectOwnerError


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id=1, name="Test Project", description="A project",
        is_archived=False, owner_id=1,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Project(**defaults)


# ── Create ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_project_success() -> None:
    project_repo = AsyncMock()
    project_repo.create.return_value = _make_project(id=1)
    project_repo.add_member = AsyncMock()

    use_case = CreateProjectUseCase(project_repo)
    result = await use_case.execute(CreateProjectInput(name="Test", description="Desc"), owner_id=1)

    assert result.id == 1
    assert result.name == "Test Project"
    assert result.owner_id == 1
    project_repo.create.assert_awaited_once()
    project_repo.add_member.assert_awaited_once_with(1, 1)


# ── Get ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_project_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1)

    project_repo.get_members.return_value = [
        ProjectMember(project_id=1, user_id=1, user_email="owner@test.com", full_name="Owner"),
        ProjectMember(project_id=1, user_id=2, user_email="member@test.com", full_name="Member"),
    ]

    use_case = GetProjectUseCase(project_repo)
    result = await use_case.execute(project_id=1, user_id=1)

    assert result.id == 1
    assert result.name == "Test Project"
    assert result.owner_id == 1
    assert result.member_count == 2


@pytest.mark.asyncio
async def test_get_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = GetProjectUseCase(project_repo)
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, user_id=1)


# ── List ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_projects_success() -> None:
    project_repo = AsyncMock()
    project_repo.list_for_user.return_value = [
        _make_project(id=1, name="Project A"),
        _make_project(id=2, name="Project B", owner_id=2),
    ]
    project_repo.get_members_for_projects.return_value = {
        1: [ProjectMember(project_id=1, user_id=1)],
        2: [ProjectMember(project_id=2, user_id=1)],
    }

    use_case = ListProjectsUseCase(project_repo)
    result = await use_case.execute(user_id=1)

    assert len(result.projects) == 2
    assert result.projects[0].name == "Project A"
    assert result.projects[1].name == "Project B"


# ── Update ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_project_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1)
    project_repo.update.return_value = _make_project(id=1, name="Updated", owner_id=1)

    use_case = UpdateProjectUseCase(project_repo)
    result = await use_case.execute(
        project_id=1,
        input_dto=UpdateProjectInput(name="Updated"),
        user_id=1,
    )

    assert result.name == "Updated"
    project_repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_project_not_owner() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1)

    use_case = UpdateProjectUseCase(project_repo)
    with pytest.raises(NotProjectOwnerError):
        await use_case.execute(
            project_id=1,
            input_dto=UpdateProjectInput(name="Hacked"),
            user_id=2,
        )
    project_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = UpdateProjectUseCase(project_repo)
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            project_id=999,
            input_dto=UpdateProjectInput(name="Whatever"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_update_project_archive() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1, is_archived=False)
    project_repo.update.return_value = _make_project(id=1, is_archived=True, owner_id=1)

    use_case = UpdateProjectUseCase(project_repo)
    result = await use_case.execute(
        project_id=1,
        input_dto=UpdateProjectInput(is_archived=True),
        user_id=1,
    )

    assert result.is_archived is True


# ── Delete ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_project_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1)

    use_case = DeleteProjectUseCase(project_repo)
    await use_case.execute(project_id=1, user_id=1)

    project_repo.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_project_not_owner() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(id=1, owner_id=1)

    use_case = DeleteProjectUseCase(project_repo)
    with pytest.raises(NotProjectOwnerError):
        await use_case.execute(project_id=1, user_id=2)
    project_repo.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = DeleteProjectUseCase(project_repo)
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, user_id=1)

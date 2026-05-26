"""Task use case tests with mocked repositories."""

from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.application.use_cases.tasks.create_task import CreateTaskUseCase
from src.application.use_cases.tasks.list_tasks import ListTasksUseCase
from src.application.use_cases.tasks.update_task import UpdateTaskUseCase
from src.application.use_cases.tasks.delete_task import DeleteTaskUseCase
from src.application.use_cases.tasks.change_status import ChangeTaskStatusUseCase
from src.application.use_cases.tasks.change_priority import ChangeTaskPriorityUseCase
from src.application.dtos.task_dtos import (
    CreateTaskInput,
    UpdateTaskInput,
    ChangeStatusInput,
    ChangePriorityInput,
)
from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.domain.entities.project import Project
from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectMemberError,
    TaskNotFoundError,
    ArchivedProjectError,
    TaskAccessDeniedError,
    InvalidAssignmentError,
)


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=1, name="Test Task", status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM, project_id=1,
        assigned_user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Task(**defaults)


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id=1, name="Test Project", description="",
        is_archived=False, owner_id=1,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Project(**defaults)


# ── Create ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_task_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.create.return_value = _make_task(id=1)

    use_case = CreateTaskUseCase(project_repo, task_repo)
    result = await use_case.execute(
        project_id=1,
        input_dto=CreateTaskInput(name="New Task"),
        user_id=1,
    )

    assert result.id == 1
    assert result.name == "Test Task"
    assert result.status == TaskStatus.PENDING
    task_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_task_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = CreateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            project_id=999,
            input_dto=CreateTaskInput(name="Task"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_create_task_not_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = False

    use_case = CreateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(
            project_id=1,
            input_dto=CreateTaskInput(name="Task"),
            user_id=2,
        )


@pytest.mark.asyncio
async def test_create_task_archived_project() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(is_archived=True)
    project_repo.is_member.return_value = True

    use_case = CreateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(ArchivedProjectError):
        await use_case.execute(
            project_id=1,
            input_dto=CreateTaskInput(name="Task"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_create_task_assign_to_non_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.side_effect = lambda pid, uid: uid == 1  # only user 1 is member

    use_case = CreateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(InvalidAssignmentError):
        await use_case.execute(
            project_id=1,
            input_dto=CreateTaskInput(name="Task", assigned_user_id=999),
            user_id=1,
        )


# ── List ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_tasks_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.list_by_project.return_value = [
        _make_task(id=1, name="Task A", assigned_user_id=1),
        _make_task(id=2, name="Task B", assigned_user_id=2),
    ]

    use_case = ListTasksUseCase(project_repo, task_repo)
    result = await use_case.execute(project_id=1, user_id=1)

    assert len(result.tasks) == 2
    assert result.tasks[0].name == "Task A"
    assert result.tasks[1].assigned_user_id == 2


@pytest.mark.asyncio
async def test_list_tasks_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = ListTasksUseCase(project_repo, AsyncMock())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, user_id=1)


@pytest.mark.asyncio
async def test_list_tasks_not_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = False

    use_case = ListTasksUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(project_id=1, user_id=2)


# ── Update ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_task_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True
    project_repo.is_member.side_effect = lambda pid, uid: True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = _make_task(id=1, assigned_user_id=1)
    task_repo.update.return_value = _make_task(id=1, name="Updated")

    use_case = UpdateTaskUseCase(project_repo, task_repo)
    result = await use_case.execute(
        project_id=1, task_id=1,
        input_dto=UpdateTaskInput(name="Updated"),
        user_id=1,
    )

    assert result.name == "Updated"
    task_repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_task_not_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = False

    use_case = UpdateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(
            project_id=1, task_id=1,
            input_dto=UpdateTaskInput(name="Hacked"),
            user_id=2,
        )


@pytest.mark.asyncio
async def test_update_task_archived_project() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(is_archived=True)
    project_repo.is_member.return_value = True

    use_case = UpdateTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(ArchivedProjectError):
        await use_case.execute(
            project_id=1, task_id=1,
            input_dto=UpdateTaskInput(name="Updated"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_update_task_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = None

    use_case = UpdateTaskUseCase(project_repo, task_repo)
    with pytest.raises(TaskNotFoundError):
        await use_case.execute(
            project_id=1, task_id=999,
            input_dto=UpdateTaskInput(name="Updated"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_update_task_access_denied() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = _make_task(id=1, assigned_user_id=2)  # assigned to user 2

    use_case = UpdateTaskUseCase(project_repo, task_repo)
    with pytest.raises(TaskAccessDeniedError):
        await use_case.execute(
            project_id=1, task_id=1,
            input_dto=UpdateTaskInput(name="Updated"),
            user_id=3,  # not owner, not assignee
        )


# ── Delete ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_task_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = _make_task(id=1, assigned_user_id=1)

    use_case = DeleteTaskUseCase(project_repo, task_repo)
    await use_case.execute(project_id=1, task_id=1, user_id=1)

    task_repo.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_task_project_not_found() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = None

    use_case = DeleteTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(project_id=999, task_id=1, user_id=1)


@pytest.mark.asyncio
async def test_delete_task_not_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = False

    use_case = DeleteTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(project_id=1, task_id=1, user_id=2)


@pytest.mark.asyncio
async def test_delete_task_archived_project() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(is_archived=True)
    project_repo.is_member.return_value = True

    use_case = DeleteTaskUseCase(project_repo, AsyncMock())
    with pytest.raises(ArchivedProjectError):
        await use_case.execute(project_id=1, task_id=1, user_id=1)


# ── Change Status ──────────────────────────────────


@pytest.mark.asyncio
async def test_change_status_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = _make_task(id=1, assigned_user_id=1)
    task_repo.update.return_value = _make_task(id=1, status=TaskStatus.IN_PROGRESS)

    use_case = ChangeTaskStatusUseCase(project_repo, task_repo)
    result = await use_case.execute(
        project_id=1, task_id=1,
        input_dto=ChangeStatusInput(status=TaskStatus.IN_PROGRESS),
        user_id=1,
    )

    assert result.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_change_status_not_member() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()
    project_repo.is_member.return_value = False

    use_case = ChangeTaskStatusUseCase(project_repo, AsyncMock())
    with pytest.raises(NotProjectMemberError):
        await use_case.execute(
            project_id=1, task_id=1,
            input_dto=ChangeStatusInput(status=TaskStatus.COMPLETED),
            user_id=2,
        )


# ── Change Priority ────────────────────────────────


@pytest.mark.asyncio
async def test_change_priority_success() -> None:
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project(owner_id=1)
    project_repo.is_member.return_value = True

    task_repo = AsyncMock()
    task_repo.get_by_id.return_value = _make_task(id=1, assigned_user_id=1)
    task_repo.update.return_value = _make_task(id=1, priority=TaskPriority.HIGH)

    use_case = ChangeTaskPriorityUseCase(project_repo, task_repo)
    result = await use_case.execute(
        project_id=1, task_id=1,
        input_dto=ChangePriorityInput(priority=TaskPriority.HIGH),
        user_id=1,
    )

    assert result.priority == TaskPriority.HIGH

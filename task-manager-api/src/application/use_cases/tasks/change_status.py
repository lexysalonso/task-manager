from datetime import datetime, timezone

from src.domain.exceptions import (
    ProjectNotFoundError,
    TaskNotFoundError,
    NotProjectMemberError,
    TaskAccessDeniedError,
    ArchivedProjectError,
)
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository
from src.application.dtos.task_dtos import ChangeStatusInput, TaskOutput


class ChangeTaskStatusUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(
        self, project_id: int, task_id: int, input_dto: ChangeStatusInput, user_id: int
    ) -> TaskOutput:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if not await self._project_repository.is_member(project_id, user_id):
            raise NotProjectMemberError()

        if project.is_archived:
            raise ArchivedProjectError()

        task = await self._task_repository.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise TaskNotFoundError()

        if project.owner_id != user_id and task.assigned_user_id != user_id:
            raise TaskAccessDeniedError()

        task.status = input_dto.status
        task.updated_at = datetime.now(timezone.utc)
        updated = await self._task_repository.update(task)
        return TaskOutput(
            id=updated.id,
            name=updated.name,
            status=updated.status,
            priority=updated.priority,
            project_id=updated.project_id,
            assigned_user_id=updated.assigned_user_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

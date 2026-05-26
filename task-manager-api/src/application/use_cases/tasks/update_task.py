from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectMemberError,
    TaskNotFoundError,
    ArchivedProjectError,
    TaskAccessDeniedError,
    InvalidAssignmentError,
)
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository
from src.application.dtos.task_dtos import UpdateTaskInput, TaskOutput
from datetime import datetime, timezone


class UpdateTaskUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(
        self, project_id: int, task_id: int, input_dto: UpdateTaskInput, user_id: int
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

        if input_dto.name is not None:
            task.name = input_dto.name
        if input_dto.priority is not None:
            task.priority = input_dto.priority
        if input_dto.assigned_user_id is not None:
            if not await self._project_repository.is_member(
                project_id, input_dto.assigned_user_id
            ):
                raise InvalidAssignmentError()
            if project.owner_id != user_id:
                raise TaskAccessDeniedError()
            task.assigned_user_id = input_dto.assigned_user_id

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

from src.domain.entities.task import Task
from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectMemberError,
    NotProjectOwnerError,
    ArchivedProjectError,
    InvalidAssignmentError,
    CannotAssignTaskError,
)
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository
from src.application.dtos.task_dtos import CreateTaskInput, TaskOutput


class CreateTaskUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(
        self, project_id: int, input_dto: CreateTaskInput, user_id: int
    ) -> TaskOutput:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if not await self._project_repository.is_member(project_id, user_id):
            raise NotProjectMemberError()

        if project.is_archived:
            raise ArchivedProjectError()

        assign_to = input_dto.assigned_user_id if input_dto.assigned_user_id is not None else user_id
        if not await self._project_repository.is_member(project_id, assign_to):
            raise InvalidAssignmentError()

        if assign_to != user_id and project.owner_id != user_id:
            raise CannotAssignTaskError()

        task = Task(
            name=input_dto.name,
            priority=input_dto.priority,
            project_id=project_id,
            assigned_user_id=assign_to,
        )
        created = await self._task_repository.create(task)
        return TaskOutput(
            id=created.id,
            name=created.name,
            status=created.status,
            priority=created.priority,
            project_id=created.project_id,
            assigned_user_id=created.assigned_user_id,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )

from src.domain.exceptions import ProjectNotFoundError, NotProjectMemberError
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository
from src.application.dtos.task_dtos import TaskOutput, TaskListOutput


class ListTasksUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(self, project_id: int, user_id: int) -> TaskListOutput:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if not await self._project_repository.is_member(project_id, user_id):
            raise NotProjectMemberError()

        tasks = await self._task_repository.list_by_project(project_id)
        outputs = [
            TaskOutput(
                id=t.id,
                name=t.name,
                status=t.status,
                priority=t.priority,
                project_id=t.project_id,
                assigned_user_id=t.assigned_user_id,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tasks
        ]
        return TaskListOutput(tasks=outputs)

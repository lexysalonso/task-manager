from src.domain.exceptions import ProjectNotFoundError, NotProjectOwnerError
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository


class DeleteProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    async def execute(self, project_id: int, user_id: int) -> None:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.owner_id != user_id:
            raise NotProjectOwnerError()

        tasks = await self._task_repository.list_by_project(project_id)
        for task in tasks:
            await self._task_repository.delete(task.id)
        await self._project_repository.delete(project_id)

from src.domain.exceptions import ProjectNotFoundError, NotProjectOwnerError
from src.domain.ports.project_repository import ProjectRepository


class DeleteProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
    ) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: int, user_id: int) -> None:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.owner_id != user_id:
            raise NotProjectOwnerError()

        await self._project_repository.delete(project_id)

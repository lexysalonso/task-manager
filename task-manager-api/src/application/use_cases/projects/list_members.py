from src.domain.exceptions import ProjectNotFoundError, NotProjectMemberError
from src.domain.ports.project_repository import ProjectRepository


class ListMembersUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: int, user_id: int) -> list[dict]:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if not await self._project_repository.is_member(project_id, user_id) and project.owner_id != user_id:
            raise NotProjectMemberError()

        members = await self._project_repository.get_members(project_id)
        return [
            {"user_id": m.user_id, "email": m.user_email, "full_name": m.full_name}
            for m in members
        ]

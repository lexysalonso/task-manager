from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectOwnerError,
    UserNotFoundError,
)
from src.domain.ports.user_repository import UserRepository
from src.domain.ports.project_repository import ProjectRepository


class AddMemberUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
    ) -> None:
        self._project_repository = project_repository
        self._user_repository = user_repository

    async def execute(self, project_id: int, target_user_id: int, current_user_id: int) -> None:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.owner_id != current_user_id:
            raise NotProjectOwnerError()

        user = await self._user_repository.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError()

        if await self._project_repository.is_member(project_id, target_user_id):
            return

        await self._project_repository.add_member(project_id, target_user_id)

from src.domain.exceptions import (
    ProjectNotFoundError,
    NotProjectOwnerError,
    UserNotFoundError,
    NotProjectMemberError,
    CannotRemoveOwnerError,
)
from src.domain.ports.user_repository import UserRepository
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository


class RemoveMemberUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        task_repository: TaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._user_repository = user_repository
        self._task_repository = task_repository

    async def execute(self, project_id: int, target_user_id: int, current_user_id: int) -> None:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.owner_id != current_user_id:
            raise NotProjectOwnerError()

        if target_user_id == project.owner_id:
            raise CannotRemoveOwnerError()

        user = await self._user_repository.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError()

        if not await self._project_repository.is_member(project_id, target_user_id):
            raise NotProjectMemberError()

        await self._task_repository.reassign_by_user(
            project_id, target_user_id, project.owner_id
        )
        await self._project_repository.remove_member(project_id, target_user_id)

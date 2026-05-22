from src.domain.exceptions import ProjectNotFoundError, NotProjectMemberError
from src.domain.ports.project_repository import ProjectRepository
from src.application.dtos.project_dtos import ProjectOutput


class GetProjectUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: int, user_id: int) -> ProjectOutput:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if not await self._project_repository.is_member(project_id, user_id):
            raise NotProjectMemberError()

        members = await self._project_repository.get_members(project_id)
        return ProjectOutput(
            id=project.id,
            name=project.name,
            description=project.description,
            is_archived=project.is_archived,
            owner_id=project.owner_id,
            created_at=project.created_at,
            member_count=len(members),
            member_ids=[m.user_id for m in members],
        )

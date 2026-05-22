from src.domain.exceptions import ProjectNotFoundError, NotProjectOwnerError
from src.domain.ports.project_repository import ProjectRepository
from src.application.dtos.project_dtos import UpdateProjectInput, CreateProjectOutput


class UpdateProjectUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(
        self, project_id: int, input_dto: UpdateProjectInput, user_id: int
    ) -> CreateProjectOutput:
        project = await self._project_repository.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.owner_id != user_id:
            raise NotProjectOwnerError()

        if input_dto.name is not None:
            project.name = input_dto.name
        if input_dto.description is not None:
            project.description = input_dto.description
        if input_dto.is_archived is not None:
            project.is_archived = input_dto.is_archived

        updated = await self._project_repository.update(project)
        return CreateProjectOutput(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            is_archived=updated.is_archived,
            owner_id=updated.owner_id,
            created_at=updated.created_at,
        )

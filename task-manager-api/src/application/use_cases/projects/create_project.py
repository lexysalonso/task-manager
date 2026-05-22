from src.domain.entities.project import Project
from src.domain.ports.project_repository import ProjectRepository
from src.application.dtos.project_dtos import CreateProjectInput, CreateProjectOutput


class CreateProjectUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, input_dto: CreateProjectInput, owner_id: int) -> CreateProjectOutput:
        project = Project(
            name=input_dto.name,
            description=input_dto.description,
            owner_id=owner_id,
        )
        created = await self._project_repository.create(project)
        await self._project_repository.add_member(created.id, owner_id)
        return CreateProjectOutput(
            id=created.id,
            name=created.name,
            description=created.description,
            is_archived=created.is_archived,
            owner_id=created.owner_id,
            created_at=created.created_at,
        )

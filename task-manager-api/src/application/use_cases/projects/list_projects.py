from src.domain.ports.project_repository import ProjectRepository
from src.application.dtos.project_dtos import ProjectOutput, ProjectListOutput


class ListProjectsUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, user_id: int) -> ProjectListOutput:
        projects = await self._project_repository.list_for_user(user_id)
        project_ids = [p.id for p in projects]
        members_by_project = await self._project_repository.get_members_for_projects(project_ids)
        outputs: list[ProjectOutput] = []
        for project in projects:
            members = members_by_project.get(project.id, [])
            outputs.append(
                ProjectOutput(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    is_archived=project.is_archived,
                    owner_id=project.owner_id,
                    created_at=project.created_at,
                    member_count=len(members),
                    member_ids=[m.user_id for m in members],
                )
            )
        return ProjectListOutput(projects=outputs)

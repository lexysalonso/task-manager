from fastapi import APIRouter, Depends, status

from src.presentation.api.v1.schemas.project_schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    AddMemberRequest,
    MemberResponse,
    ProjectResponse,
    ProjectListResponse,
)
from src.presentation.api.v1.dependencies import (
    get_current_user_id,
    get_project_repo,
    get_create_project_use_case,
    get_get_project_use_case,
    get_list_projects_use_case,
    get_update_project_use_case,
    get_delete_project_use_case,
    get_add_member_use_case,
    get_remove_member_use_case,
)
from src.application.use_cases.projects import (
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
    DeleteProjectUseCase,
    AddMemberUseCase,
    RemoveMemberUseCase,
)
from src.application.dtos.project_dtos import CreateProjectInput, UpdateProjectInput
from src.infrastructure.db.repositories import SqlAlchemyProjectRepository

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List user projects",
    description="Returns all projects where the authenticated user is owner or member",
)
async def list_projects(
    user_id: int = Depends(get_current_user_id),
    use_case: ListProjectsUseCase = Depends(get_list_projects_use_case),
) -> ProjectListResponse:
    result = await use_case.execute(user_id)
    return ProjectListResponse(
        projects=[
            ProjectResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                is_archived=p.is_archived,
                owner_id=p.owner_id,
                created_at=p.created_at,
                member_count=p.member_count,
                member_ids=p.member_ids,
            )
            for p in result.projects
        ]
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Creates a new project. The creator becomes the owner.",
)
async def create_project(
    body: CreateProjectRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),
) -> ProjectResponse:
    result = await use_case.execute(
        CreateProjectInput(name=body.name, description=body.description),
        owner_id=user_id,
    )
    return ProjectResponse(
        id=result.id,
        name=result.name,
        description=result.description,
        is_archived=result.is_archived,
        owner_id=result.owner_id,
        created_at=result.created_at,
        member_count=1,
        member_ids=[user_id],
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
    description="Returns project details. Members only.",
)
async def get_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: GetProjectUseCase = Depends(get_get_project_use_case),
) -> ProjectResponse:
    result = await use_case.execute(project_id, user_id)
    return ProjectResponse(
        id=result.id,
        name=result.name,
        description=result.description,
        is_archived=result.is_archived,
        owner_id=result.owner_id,
        created_at=result.created_at,
        member_count=result.member_count,
        member_ids=result.member_ids,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Updates project details. Owner only.",
)
async def update_project(
    project_id: int,
    body: UpdateProjectRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: UpdateProjectUseCase = Depends(get_update_project_use_case),
) -> ProjectResponse:
    result = await use_case.execute(
        project_id,
        UpdateProjectInput(
            name=body.name,
            description=body.description,
            is_archived=body.is_archived,
        ),
        user_id,
    )
    return ProjectResponse(
        id=result.id,
        name=result.name,
        description=result.description,
        is_archived=result.is_archived,
        owner_id=result.owner_id,
        created_at=result.created_at,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Deletes a project and all its tasks. Owner only.",
)
async def delete_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: DeleteProjectUseCase = Depends(get_delete_project_use_case),
) -> None:
    await use_case.execute(project_id, user_id)


@router.get(
    "/{project_id}/members",
    response_model=list[MemberResponse],
    summary="List project members",
    description="Returns all members of a project with their details.",
)
async def list_members(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    project_repo: SqlAlchemyProjectRepository = Depends(get_project_repo),
) -> list[MemberResponse]:
    result = await project_repo.get_by_id(project_id)
    if not result:
        from src.domain.exceptions import ProjectNotFoundError
        raise ProjectNotFoundError()
    if not await project_repo.is_member(project_id, user_id) and result.owner_id != user_id:
        from src.domain.exceptions import NotProjectMemberError
        raise NotProjectMemberError()
    members = await project_repo.get_members(project_id)
    return [
        MemberResponse(user_id=m.user_id, email=m.user_email, full_name=m.full_name)
        for m in members
    ]


@router.post(
    "/{project_id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Add member to project",
    description="Adds a user as a project member. Owner only.",
)
async def add_member(
    project_id: int,
    body: AddMemberRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: AddMemberUseCase = Depends(get_add_member_use_case),
) -> None:
    await use_case.execute(project_id, body.user_id, user_id)


@router.delete(
    "/{project_id}/members/{target_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from project",
    description="Removes a member. Their tasks are reassigned to the owner. Owner only.",
)
async def remove_member(
    project_id: int,
    target_user_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: RemoveMemberUseCase = Depends(get_remove_member_use_case),
) -> None:
    await use_case.execute(project_id, target_user_id, user_id)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import get_db_session
from src.infrastructure.db.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyTaskRepository,
)
from src.infrastructure.security.password_service import PasswordService
from src.domain.ports.user_repository import UserRepository
from src.domain.ports.project_repository import ProjectRepository
from src.domain.ports.task_repository import TaskRepository
from src.domain.ports.password_service import PasswordService as PasswordServicePort
from src.domain.ports.token_service import TokenService
from src.application.use_cases.auth import RegisterUserUseCase, LoginUserUseCase
from src.application.use_cases.projects import (
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
    DeleteProjectUseCase,
    AddMemberUseCase,
    RemoveMemberUseCase,
    ListMembersUseCase,
)
from src.application.use_cases.users import SearchUsersUseCase
from src.application.use_cases.tasks import (
    CreateTaskUseCase,
    ListTasksUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    ChangeTaskStatusUseCase,
    ChangeTaskPriorityUseCase,
)

security_scheme = HTTPBearer()


def get_password_service() -> PasswordServicePort:
    return PasswordService()


def get_jwt_service() -> TokenService:
    return JwtService()


async def get_user_repo(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


async def get_project_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ProjectRepository:
    return SqlAlchemyProjectRepository(session)


async def get_task_repo(
    session: AsyncSession = Depends(get_db_session),
) -> TaskRepository:
    return SqlAlchemyTaskRepository(session)


async def get_register_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    pwd_service: PasswordServicePort = Depends(get_password_service),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, pwd_service)


async def get_login_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    pwd_service: PasswordServicePort = Depends(get_password_service),
    jwt_service: TokenService = Depends(get_jwt_service),
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo, pwd_service, jwt_service)


async def get_create_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repo)


async def get_get_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> GetProjectUseCase:
    return GetProjectUseCase(project_repo)


async def get_list_projects_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> ListProjectsUseCase:
    return ListProjectsUseCase(project_repo)


async def get_update_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(project_repo)


async def get_delete_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(project_repo)


async def get_add_member_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> AddMemberUseCase:
    return AddMemberUseCase(project_repo, user_repo)


async def get_list_members_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> ListMembersUseCase:
    return ListMembersUseCase(project_repo)


async def get_search_users_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
) -> SearchUsersUseCase:
    return SearchUsersUseCase(user_repo)


async def get_remove_member_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> RemoveMemberUseCase:
    return RemoveMemberUseCase(project_repo, user_repo, task_repo)


async def get_create_task_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> CreateTaskUseCase:
    return CreateTaskUseCase(project_repo, task_repo)


async def get_list_tasks_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> ListTasksUseCase:
    return ListTasksUseCase(project_repo, task_repo)


async def get_update_task_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(project_repo, task_repo)


async def get_delete_task_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> DeleteTaskUseCase:
    return DeleteTaskUseCase(project_repo, task_repo)


async def get_change_status_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> ChangeTaskStatusUseCase:
    return ChangeTaskStatusUseCase(project_repo, task_repo)


async def get_change_priority_use_case(
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
) -> ChangeTaskPriorityUseCase:
    return ChangeTaskPriorityUseCase(project_repo, task_repo)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    jwt_service: TokenService = Depends(get_jwt_service),
) -> int:
    token = credentials.credentials
    payload = jwt_service.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return int(user_id)

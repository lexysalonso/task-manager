from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project import Project, ProjectMember
from src.domain.exceptions import ProjectNotFoundError
from src.domain.ports.project_repository import ProjectRepository
from src.infrastructure.db.models.project_model import ProjectModel, ProjectMemberModel
from src.infrastructure.db.models.user_model import UserModel


class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project: Project) -> Project:
        model = ProjectModel(
            name=project.name,
            description=project.description,
            is_archived=project.is_archived,
            owner_id=project.owner_id,
        )
        self._session.add(model)
        await self._session.flush()
        return Project(
            id=model.id,
            name=model.name,
            description=model.description or "",
            is_archived=model.is_archived,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Project(
            id=model.id,
            name=model.name,
            description=model.description or "",
            is_archived=model.is_archived,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )

    async def list_for_user(self, user_id: int) -> list[Project]:
        subq = select(ProjectMemberModel.project_id).where(
            ProjectMemberModel.user_id == user_id
        )
        result = await self._session.execute(
            select(ProjectModel)
            .where(
                (ProjectModel.owner_id == user_id) | (ProjectModel.id.in_(subq))
            )
            .order_by(ProjectModel.created_at.desc())
        )
        models = result.scalars().all()
        return [
            Project(
                id=m.id,
                name=m.name,
                description=m.description or "",
                is_archived=m.is_archived,
                owner_id=m.owner_id,
                created_at=m.created_at,
            )
            for m in models
        ]

    async def update(self, project: Project) -> Project:
        model = await self._session.get(ProjectModel, project.id)
        if not model:
            raise ProjectNotFoundError()
        model.name = project.name
        model.description = project.description
        model.is_archived = project.is_archived
        await self._session.flush()
        return Project(
            id=model.id,
            name=model.name,
            description=model.description or "",
            is_archived=model.is_archived,
            owner_id=model.owner_id,
            created_at=model.created_at,
        )

    async def delete(self, project_id: int) -> None:
        await self._session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )

    async def add_member(self, project_id: int, user_id: int) -> None:
        model = ProjectMemberModel(project_id=project_id, user_id=user_id)
        self._session.add(model)
        await self._session.flush()

    async def remove_member(self, project_id: int, user_id: int) -> None:
        await self._session.execute(
            delete(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )

    async def get_members(self, project_id: int) -> list[ProjectMember]:
        result = await self._session.execute(
            select(ProjectMemberModel, UserModel.email, UserModel.full_name)
            .join(UserModel, ProjectMemberModel.user_id == UserModel.id)
            .where(ProjectMemberModel.project_id == project_id)
        )
        rows = result.all()
        return [
            ProjectMember(project_id=pm.project_id, user_id=pm.user_id, user_email=email, full_name=full_name)
            for pm, email, full_name in rows
        ]

    async def get_members_for_projects(self, project_ids: list[int]) -> dict[int, list[ProjectMember]]:
        if not project_ids:
            return {}
        result = await self._session.execute(
            select(ProjectMemberModel, UserModel.email, UserModel.full_name)
            .join(UserModel, ProjectMemberModel.user_id == UserModel.id)
            .where(ProjectMemberModel.project_id.in_(project_ids))
        )
        rows = result.all()
        members_by_project: dict[int, list[ProjectMember]] = {}
        for pm, email, full_name in rows:
            member = ProjectMember(project_id=pm.project_id, user_id=pm.user_id, user_email=email, full_name=full_name)
            members_by_project.setdefault(pm.project_id, []).append(member)
        return members_by_project

    async def is_member(self, project_id: int, user_id: int) -> bool:
        result = await self._session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

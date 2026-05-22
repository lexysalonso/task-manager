from abc import ABC, abstractmethod

from src.domain.entities.project import Project, ProjectMember


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, project_id: int) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_user(self, user_id: int) -> list[Project]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, project_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_member(self, project_id: int, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_member(self, project_id: int, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_members(self, project_id: int) -> list[ProjectMember]:
        raise NotImplementedError

    @abstractmethod
    async def is_member(self, project_id: int, user_id: int) -> bool:
        raise NotImplementedError

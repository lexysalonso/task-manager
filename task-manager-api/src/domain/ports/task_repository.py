from abc import ABC, abstractmethod

from src.domain.entities.task import Task


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_project(self, project_id: int) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, task_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def reassign_by_user(self, project_id: int, from_user_id: int, to_user_id: int) -> None:
        raise NotImplementedError

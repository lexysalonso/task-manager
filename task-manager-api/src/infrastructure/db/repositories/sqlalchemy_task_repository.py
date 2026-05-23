from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task import Task
from src.domain.ports.task_repository import TaskRepository
from src.infrastructure.db.models.task_model import TaskModel


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, task: Task) -> Task:
        model = TaskModel(
            name=task.name,
            status=task.status,
            priority=task.priority,
            project_id=task.project_id,
            assigned_user_id=task.assigned_user_id,
        )
        self._session.add(model)
        await self._session.flush()
        return Task(
            id=model.id,
            name=model.name,
            status=model.status,
            priority=model.priority,
            project_id=model.project_id,
            assigned_user_id=model.assigned_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self._session.execute(select(TaskModel).where(TaskModel.id == task_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Task(
            id=model.id,
            name=model.name,
            status=model.status,
            priority=model.priority,
            project_id=model.project_id,
            assigned_user_id=model.assigned_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_project(self, project_id: int) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel)
            .where(TaskModel.project_id == project_id)
            .order_by(TaskModel.created_at.desc())
        )
        models = result.scalars().all()
        return [
            Task(
                id=m.id,
                name=m.name,
                status=m.status,
                priority=m.priority,
                project_id=m.project_id,
                assigned_user_id=m.assigned_user_id,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    async def update(self, task: Task) -> Task:
        model = await self._session.get(TaskModel, task.id)
        if not model:
            raise ValueError("Task not found")
        model.name = task.name
        model.status = task.status
        model.priority = task.priority
        model.assigned_user_id = task.assigned_user_id
        model.updated_at = task.updated_at
        await self._session.flush()
        return Task(
            id=model.id,
            name=model.name,
            status=model.status,
            priority=model.priority,
            project_id=model.project_id,
            assigned_user_id=model.assigned_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def delete(self, task_id: int) -> None:
        await self._session.execute(delete(TaskModel).where(TaskModel.id == task_id))

    async def reassign_by_user(
        self, project_id: int, from_user_id: int, to_user_id: int
    ) -> None:
        await self._session.execute(
            update(TaskModel)
            .where(
                TaskModel.project_id == project_id,
                TaskModel.assigned_user_id == from_user_id,
            )
            .values(assigned_user_id=to_user_id)
        )

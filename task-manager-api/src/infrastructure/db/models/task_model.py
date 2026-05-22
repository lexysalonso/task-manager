from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.task import TaskStatus, TaskPriority
from src.infrastructure.db.models.base import Base


def _enum_values(enum_class: type) -> list[str]:
    return [e.value for e in enum_class]


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=_enum_values, name="task_status"),
        default=TaskStatus.PENDING, nullable=False,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=_enum_values, name="task_priority"),
        default=TaskPriority.MEDIUM, nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

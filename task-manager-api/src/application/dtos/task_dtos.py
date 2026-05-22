from dataclasses import dataclass, field
from datetime import datetime

from src.domain.entities.task import TaskPriority, TaskStatus


@dataclass
class CreateTaskInput:
    name: str
    assigned_user_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


@dataclass
class TaskOutput:
    id: int
    name: str
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assigned_user_id: int | None
    created_at: datetime
    updated_at: datetime


@dataclass
class TaskListOutput:
    tasks: list[TaskOutput]


@dataclass
class UpdateTaskInput:
    name: str | None = None
    assigned_user_id: int | None = None
    priority: TaskPriority | None = None


@dataclass
class ChangeStatusInput:
    status: TaskStatus


@dataclass
class ChangePriorityInput:
    priority: TaskPriority

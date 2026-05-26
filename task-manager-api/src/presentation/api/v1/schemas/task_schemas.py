from datetime import datetime

from pydantic import BaseModel, field_validator

from src.domain.entities.task import TaskPriority, TaskStatus


class CreateTaskRequest(BaseModel):
    name: str
    assigned_user_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 200:
            raise ValueError("El nombre debe tener entre 3 y 200 caracteres")
        return v


class UpdateTaskRequest(BaseModel):
    name: str | None = None
    assigned_user_id: int | None = None
    priority: TaskPriority | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and (len(v) < 3 or len(v) > 200):
            raise ValueError("El nombre debe tener entre 3 y 200 caracteres")
        return v


class ChangeStatusRequest(BaseModel):
    status: TaskStatus


class ChangePriorityRequest(BaseModel):
    priority: TaskPriority


class TaskResponse(BaseModel):
    id: int
    name: str
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assigned_user_id: int | None
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    pagination: PaginationMeta

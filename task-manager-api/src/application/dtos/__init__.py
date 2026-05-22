from .auth_dtos import RegisterInput, RegisterOutput, LoginInput, LoginOutput
from .project_dtos import (
    CreateProjectInput,
    CreateProjectOutput,
    ProjectOutput,
    ProjectListOutput,
    UpdateProjectInput,
    AddMemberInput,
)
from .task_dtos import (
    CreateTaskInput,
    TaskOutput,
    TaskListOutput,
    UpdateTaskInput,
    ChangeStatusInput,
    ChangePriorityInput,
)

__all__ = [
    "RegisterInput",
    "RegisterOutput",
    "LoginInput",
    "LoginOutput",
    "CreateProjectInput",
    "CreateProjectOutput",
    "ProjectOutput",
    "ProjectListOutput",
    "UpdateProjectInput",
    "AddMemberInput",
    "CreateTaskInput",
    "TaskOutput",
    "TaskListOutput",
    "UpdateTaskInput",
    "ChangeStatusInput",
    "ChangePriorityInput",
]

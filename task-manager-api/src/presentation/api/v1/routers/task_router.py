from fastapi import APIRouter, Depends, status

from src.presentation.api.v1.schemas.task_schemas import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ChangeStatusRequest,
    ChangePriorityRequest,
    TaskResponse,
    TaskListResponse,
)
from src.presentation.api.v1.dependencies import (
    get_current_user_id,
    get_create_task_use_case,
    get_list_tasks_use_case,
    get_update_task_use_case,
    get_delete_task_use_case,
    get_change_status_use_case,
    get_change_priority_use_case,
)
from src.application.use_cases.tasks import (
    CreateTaskUseCase,
    ListTasksUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    ChangeTaskStatusUseCase,
    ChangeTaskPriorityUseCase,
)
from src.application.dtos.task_dtos import (
    CreateTaskInput,
    UpdateTaskInput,
    ChangeStatusInput,
    ChangePriorityInput,
)

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks",
    description="Returns all tasks in a project. Members only.",
)
async def list_tasks(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: ListTasksUseCase = Depends(get_list_tasks_use_case),
) -> TaskListResponse:
    result = await use_case.execute(project_id, user_id)
    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=t.id,
                name=t.name,
                status=t.status,
                priority=t.priority,
                project_id=t.project_id,
                assigned_user_id=t.assigned_user_id,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in result.tasks
        ]
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Creates a new task in the project. Members only. Archived projects are read-only.",
)
async def create_task(
    project_id: int,
    body: CreateTaskRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        project_id,
        CreateTaskInput(
            name=body.name,
            assigned_user_id=body.assigned_user_id,
            priority=body.priority,
        ),
        user_id,
    )
    return TaskResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        priority=result.priority,
        project_id=result.project_id,
        assigned_user_id=result.assigned_user_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Updates task details. Owner can update any task; members can update their own. Archived projects are read-only.",
)
async def update_task(
    project_id: int,
    task_id: int,
    body: UpdateTaskRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        project_id,
        task_id,
        UpdateTaskInput(
            name=body.name,
            assigned_user_id=body.assigned_user_id,
            priority=body.priority,
        ),
        user_id,
    )
    return TaskResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        priority=result.priority,
        project_id=result.project_id,
        assigned_user_id=result.assigned_user_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Change task status",
    description="Changes the status of a task. Owner can change any; members can change their own. Archived projects are read-only.",
)
async def change_task_status(
    project_id: int,
    task_id: int,
    body: ChangeStatusRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChangeTaskStatusUseCase = Depends(get_change_status_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        project_id,
        task_id,
        ChangeStatusInput(status=body.status),
        user_id,
    )
    return TaskResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        priority=result.priority,
        project_id=result.project_id,
        assigned_user_id=result.assigned_user_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.patch(
    "/{task_id}/priority",
    response_model=TaskResponse,
    summary="Change task priority",
    description="Changes the priority of a task. Owner can change any; members can change their own. Archived projects are read-only.",
)
async def change_task_priority(
    project_id: int,
    task_id: int,
    body: ChangePriorityRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChangeTaskPriorityUseCase = Depends(get_change_priority_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        project_id,
        task_id,
        ChangePriorityInput(priority=body.priority),
        user_id,
    )
    return TaskResponse(
        id=result.id,
        name=result.name,
        status=result.status,
        priority=result.priority,
        project_id=result.project_id,
        assigned_user_id=result.assigned_user_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Deletes a task. Owner can delete any; members can delete their own. Archived projects are read-only.",
)
async def delete_task(
    project_id: int,
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case),
) -> None:
    await use_case.execute(project_id, task_id, user_id)

from fastapi import APIRouter, Depends, Query

from src.presentation.api.v1.schemas.user_schemas import UserSearchResponse
from src.presentation.api.v1.dependencies import get_current_user_id, get_search_users_use_case
from src.application.use_cases.users import SearchUsersUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/search",
    response_model=list[UserSearchResponse],
    summary="Search users",
    description="Search users by email or full name. Requires authentication.",
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    user_id: int = Depends(get_current_user_id),
    use_case: SearchUsersUseCase = Depends(get_search_users_use_case),
) -> list[UserSearchResponse]:
    result = await use_case.execute(q)
    return [UserSearchResponse(id=u.id, email=u.email, full_name=u.full_name) for u in result]

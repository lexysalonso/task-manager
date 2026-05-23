from fastapi import APIRouter, Depends, Query

from src.presentation.api.v1.dependencies import get_user_repo, get_current_user_id
from src.infrastructure.db.repositories import SqlAlchemyUserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/search",
    summary="Search users",
    description="Search users by email or full name. Requires authentication.",
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    user_id: int = Depends(get_current_user_id),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repo),
) -> list[dict]:
    users = await user_repo.search(q)
    return [
        {"id": u.id, "email": u.email, "full_name": u.full_name}
        for u in users
    ]

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the API",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

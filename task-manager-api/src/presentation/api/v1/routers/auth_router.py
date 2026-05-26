from fastapi import APIRouter, Depends, Request, status

from src.application.use_cases.auth import RegisterUserUseCase, LoginUserUseCase
from src.application.dtos.auth_dtos import RegisterInput, LoginInput
from src.presentation.api.v1.schemas.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
)
from src.presentation.api.v1.dependencies import (
    get_register_use_case,
    get_login_use_case,
    get_jwt_service,
)
from src.domain.ports.token_service import TokenService
from src.infrastructure.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account and returns a JWT access token",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
    jwt_service: TokenService = Depends(get_jwt_service),
) -> AuthResponse:
    output = await use_case.execute(
        RegisterInput(email=body.email, full_name=body.full_name, password=body.password)
    )
    token = jwt_service.create_access_token(data={"sub": str(output.id), "email": output.email})
    return AuthResponse(
        access_token=token,
        user=UserResponse(id=output.id, email=output.email, full_name=output.full_name),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user",
    description="Validates credentials and returns a JWT access token",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
) -> AuthResponse:
    output = await use_case.execute(LoginInput(email=body.email, password=body.password))
    return AuthResponse(
        access_token=output.access_token,
        user=UserResponse(id=output.id, email=output.email, full_name=output.full_name),
    )

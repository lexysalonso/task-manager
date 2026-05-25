from src.domain.exceptions import InvalidCredentialsError
from src.domain.ports.user_repository import UserRepository
from src.domain.ports.password_service import PasswordService
from src.domain.ports.token_service import TokenService
from src.application.dtos.auth_dtos import LoginInput, LoginOutput


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def execute(self, input_dto: LoginInput) -> LoginOutput:
        user = await self._user_repository.get_by_email(input_dto.email)
        if not user or not self._password_service.verify_password(
            input_dto.password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        token = self._jwt_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return LoginOutput(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            access_token=token,
        )

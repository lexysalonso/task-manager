from src.domain.entities.user import User
from src.domain.exceptions import DuplicateEmailError
from src.domain.ports.user_repository import UserRepository
from src.application.dtos.auth_dtos import RegisterInput, RegisterOutput
from src.infrastructure.security.password_service import PasswordService


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service

    async def execute(self, input_dto: RegisterInput) -> RegisterOutput:
        existing = await self._user_repository.get_by_email(input_dto.email)
        if existing:
            raise DuplicateEmailError()

        hashed = self._password_service.hash_password(input_dto.password)
        user = User(
            email=input_dto.email,
            full_name=input_dto.full_name,
            hashed_password=hashed,
        )
        created = await self._user_repository.create(user)
        return RegisterOutput(id=created.id, email=created.email, full_name=created.full_name)

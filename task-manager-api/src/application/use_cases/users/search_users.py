from src.domain.ports.user_repository import UserRepository
from src.application.dtos.user_dtos import UserSearchResult


class SearchUsersUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, query: str) -> list[UserSearchResult]:
        users = await self._user_repository.search(query)
        return [
            UserSearchResult(id=u.id, email=u.email, full_name=u.full_name)
            for u in users
        ]

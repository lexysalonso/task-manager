from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.ports.user_repository import UserRepository
from src.infrastructure.db.models.user_model import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
        )
        self._session.add(model)
        await self._session.flush()
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )

    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        if not user_ids:
            return []
        result = await self._session.execute(
            select(UserModel).where(UserModel.id.in_(user_ids))
        )
        models = result.scalars().all()
        id_map = {m.id: m for m in models}
        return [
            User(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                hashed_password=m.hashed_password,
                created_at=m.created_at,
            )
            for uid in user_ids
            if (m := id_map.get(uid))
        ]

    async def search(self, query: str, limit: int = 20) -> list[User]:
        stmt = (
            select(UserModel)
            .where(
                UserModel.email.ilike(f"%{query}%") | UserModel.full_name.ilike(f"%{query}%")
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [
            User(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                hashed_password=m.hashed_password,
                created_at=m.created_at,
            )
            for m in models
        ]

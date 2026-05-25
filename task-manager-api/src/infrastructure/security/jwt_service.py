from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.config import settings
from src.domain.ports.token_service import TokenService


class JwtService(TokenService):
    def create_access_token(self, data: dict[str, str | int]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode["exp"] = expire
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def decode_access_token(self, token: str) -> dict[str, str | int] | None:
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None

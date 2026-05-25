from abc import ABC, abstractmethod


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict[str, str | int]) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, str | int] | None:
        raise NotImplementedError

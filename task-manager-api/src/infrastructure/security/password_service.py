import bcrypt

from src.domain.ports.password_service import PasswordService as PasswordServicePort


class PasswordService(PasswordServicePort):
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

from dataclasses import dataclass


@dataclass
class RegisterInput:
    email: str
    full_name: str
    password: str


@dataclass
class RegisterOutput:
    id: int
    email: str
    full_name: str


@dataclass
class LoginInput:
    email: str
    password: str


@dataclass
class LoginOutput:
    id: int
    email: str
    full_name: str
    access_token: str
    token_type: str = "bearer"

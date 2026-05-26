from dataclasses import dataclass


@dataclass
class UserSearchResult:
    id: int
    email: str
    full_name: str

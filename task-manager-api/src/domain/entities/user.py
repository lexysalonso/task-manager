from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    id: int | None = None
    email: str = ""
    full_name: str = ""
    hashed_password: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

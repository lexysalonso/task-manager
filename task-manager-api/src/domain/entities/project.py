from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProjectMember:
    project_id: int
    user_id: int
    user_email: str = ""


@dataclass
class Project:
    id: int | None = None
    name: str = ""
    description: str = ""
    is_archived: bool = False
    owner_id: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    members: list[ProjectMember] = field(default_factory=list)

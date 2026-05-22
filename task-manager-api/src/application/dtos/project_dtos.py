from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CreateProjectInput:
    name: str
    description: str = ""


@dataclass
class CreateProjectOutput:
    id: int
    name: str
    description: str
    is_archived: bool
    owner_id: int
    created_at: datetime


@dataclass
class ProjectOutput:
    id: int
    name: str
    description: str
    is_archived: bool
    owner_id: int
    created_at: datetime
    member_count: int = 0
    member_ids: list[int] = field(default_factory=list)


@dataclass
class ProjectListOutput:
    projects: list[ProjectOutput]


@dataclass
class UpdateProjectInput:
    name: str | None = None
    description: str | None = None
    is_archived: bool | None = None


@dataclass
class AddMemberInput:
    user_id: int

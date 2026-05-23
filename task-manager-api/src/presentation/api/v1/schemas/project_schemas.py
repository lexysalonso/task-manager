from datetime import datetime

from pydantic import BaseModel, field_validator


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 100:
            raise ValueError("El nombre debe tener entre 3 y 100 caracteres")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError("La descripción no debe exceder los 500 caracteres")
        return v


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    is_archived: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and (len(v) < 3 or len(v) > 100):
            raise ValueError("El nombre debe tener entre 3 y 100 caracteres")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("La descripción no debe exceder los 500 caracteres")
        return v


class AddMemberRequest(BaseModel):
    user_id: int


class MemberResponse(BaseModel):
    user_id: int
    email: str
    full_name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    is_archived: bool
    owner_id: int
    created_at: datetime
    member_count: int = 0
    member_ids: list[int] = []


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]

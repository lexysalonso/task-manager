from pydantic import BaseModel


class UserSearchResponse(BaseModel):
    id: int
    email: str
    full_name: str

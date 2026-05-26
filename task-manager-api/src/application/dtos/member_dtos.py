from dataclasses import dataclass


@dataclass
class MemberDTO:
    user_id: int
    email: str
    full_name: str

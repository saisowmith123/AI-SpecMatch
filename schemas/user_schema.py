from pydantic import BaseModel
from typing import Optional


class UserSchema(BaseModel):
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    income_level: Optional[str] = None
    location: Optional[str] = None

    preferences: Optional[str] = None
    interests: Optional[str] = None
    purchase_history: Optional[str] = None

    budget_range: Optional[str] = None
    tech_savviness: Optional[str] = None

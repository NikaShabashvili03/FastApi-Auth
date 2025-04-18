from pydantic import BaseModel, field_validator
from datetime import datetime


class BlackListCreate(BaseModel):
    ip: str
    reason: str

    @field_validator("reason")
    def reson_min_length(cls, v: str) -> str:
        if len(v) < 25:
            raise ValueError("Reason must be at least 25 characters long.")
        return v


class BlackListOut(BaseModel):
    id: int
    ip: str
    reason: str
    created_at: datetime

    class Config:
        orm_mode = True
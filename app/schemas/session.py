from pydantic import BaseModel
from datetime import datetime

class SessionOut(BaseModel):
    id: str
    created_at: datetime

    
    class Config:
        orm_mode = True
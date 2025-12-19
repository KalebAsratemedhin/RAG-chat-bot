from datetime import datetime
from pydantic import BaseModel
# Vote Schemas
class VoteCreate(BaseModel):
    votable_type: str
    votable_id: int
    vote_type: str

class VoteOut(BaseModel):
    id: int
    user_id: int
    votable_type: str
    votable_id: int
    vote_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

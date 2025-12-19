from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr

# Answer Schemas
class AnswerBase(BaseModel):
    content: constr(min_length=10)

class AnswerCreate(AnswerBase):
    question_id: int

class AnswerCreateRequest(BaseModel):
    content: str

class AnswerUpdateRequest(BaseModel):
    content: Optional[str] = None

class AnswerUpdate(BaseModel):
    content: Optional[constr(min_length=10)] = None

class AnswerOut(AnswerBase):
    id: int
    question_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    is_accepted: bool
    vote_score: int = 0
    
    class Config:
        from_attributes = True

class AnswerDetail(AnswerOut):
    author_email: str
    user_vote: Optional[str] = None

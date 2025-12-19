from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr
from app.schemas.answers import AnswerOut

# Question Schemas
class QuestionBase(BaseModel):
    title: constr(min_length=5, max_length=255)
    content: constr(min_length=10)

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[constr(min_length=5, max_length=255)] = None
    content: Optional[constr(min_length=10)] = None
    is_solved: Optional[bool] = None

class QuestionOut(QuestionBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    is_solved: bool
    vote_score: int = 0  
    answer_count: int = 0  
    
    class Config:
        from_attributes = True

class QuestionDetail(QuestionOut):
    author_email: str
    answers: List['AnswerOut'] = []
    user_vote: Optional[str] = None

QuestionDetail.model_rebuild()
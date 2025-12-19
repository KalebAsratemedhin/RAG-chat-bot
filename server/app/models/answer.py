from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    votes = relationship(
        "Vote", 
        back_populates="answer", 
        cascade="all, delete-orphan",
        primaryjoin="and_(Vote.votable_type=='answer', foreign(Vote.votable_id)==Answer.id)"
    )
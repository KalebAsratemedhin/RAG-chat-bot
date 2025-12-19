from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, foreign
from app.core.database import Base

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    votable_type = Column(String(20), nullable=False)
    votable_id = Column(Integer, nullable=False)
    vote_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="votes")
    question = relationship("Question", back_populates="votes", 
                           primaryjoin="and_(Vote.votable_type=='question', foreign(Vote.votable_id)==Question.id)")
    answer = relationship("Answer", back_populates="votes",
                         primaryjoin="and_(Vote.votable_type=='answer', foreign(Vote.votable_id)==Answer.id)")
    
    # Unique constraint: one vote per user per question/answer
    __table_args__ = (
        UniqueConstraint('user_id', 'votable_type', 'votable_id', name='unique_user_vote'),
    )
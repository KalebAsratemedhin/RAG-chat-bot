from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vote import Vote
from app.models.question import Question
from app.models.answer import Answer

class VoteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_or_update_vote(
        self, 
        votable_type: str, 
        votable_id: int, 
        vote_type: str, 
        user_id: int
    ) -> Vote:
        # Validate votable_type
        if votable_type not in ['question', 'answer']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="votable_type must be 'question' or 'answer'"
            )
        
        # Validate vote_type
        if vote_type not in ['upvote', 'downvote']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vote_type must be 'upvote' or 'downvote'"
            )
        
        # Verify the question/answer exists
        if votable_type == 'question':
            votable = self.db.query(Question).filter(Question.id == votable_id).first()
        else:
            votable = self.db.query(Answer).filter(Answer.id == votable_id).first()
        
        if not votable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{votable_type.capitalize()} not found"
            )
        
        # Check if user is voting on their own content
        if votable_type == 'question' and votable.author_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot vote on your own question"
            )
        if votable_type == 'answer' and votable.author_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot vote on your own answer"
            )
        
        # Check if vote already exists
        existing_vote = self.db.query(Vote).filter(
            Vote.user_id == user_id,
            Vote.votable_type == votable_type,
            Vote.votable_id == votable_id
        ).first()
        
        if existing_vote:
            # If same vote type, remove it (toggle off)
            if existing_vote.vote_type == vote_type:
                self.db.delete(existing_vote)
                self.db.commit()
                return None  # Vote removed
            else:
                # Update to opposite vote type
                existing_vote.vote_type = vote_type
                self.db.commit()
                self.db.refresh(existing_vote)
                return existing_vote
        else:
            # Create new vote
            vote = Vote(
                user_id=user_id,
                votable_type=votable_type,
                votable_id=votable_id,
                vote_type=vote_type
            )
            self.db.add(vote)
            self.db.commit()
            self.db.refresh(vote)
            return vote

    def remove_vote(self, votable_type: str, votable_id: int, user_id: int) -> None:
        vote = self.db.query(Vote).filter(
            Vote.user_id == user_id,
            Vote.votable_type == votable_type,
            Vote.votable_id == votable_id
        ).first()
        
        if vote:
            self.db.delete(vote)
            self.db.commit()
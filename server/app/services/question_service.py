from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException, status

from app.models.question import Question
from app.models.answer import Answer
from app.models.vote import Vote
from app.schemas.questions import QuestionCreate, QuestionUpdate

class QuestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_question(self, question_data: QuestionCreate, author_id: int) -> Question:
        question = Question(
            title=question_data.title,
            content=question_data.content,
            author_id=author_id
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_question(self, question_id: int, user_id: Optional[int] = None) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_questions(
        self, 
        skip: int = 0, 
        limit: int = 20,
        is_solved: Optional[bool] = None,
        author_id: Optional[int] = None
    ) -> List[Question]:
        query = self.db.query(Question)
        
        if is_solved is not None:
            query = query.filter(Question.is_solved == is_solved)
        if author_id is not None:
            query = query.filter(Question.author_id == author_id)
        
        return query.order_by(Question.created_at.desc()).offset(skip).limit(limit).all()

    def update_question(
        self, 
        question_id: int, 
        question_data: QuestionUpdate, 
        author_id: int
    ) -> Question:
        question = self.get_question(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        if question.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this question"
            )
        
        update_data = question_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: int, author_id: int) -> None:
        question = self.get_question(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        if question.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this question"
            )
        
        self.db.delete(question)
        self.db.commit()

    def get_question_vote_score(self, question_id: int) -> int:
        result = self.db.query(
            func.sum(
                case(
                    (Vote.vote_type == 'upvote', 1),
                    (Vote.vote_type == 'downvote', -1),
                    else_=0
                )
            )
        ).filter(
            Vote.votable_type == 'question',
            Vote.votable_id == question_id
        ).scalar()
        return result or 0

    def get_user_vote(self, question_id: int, user_id: int) -> Optional[str]:
        vote = self.db.query(Vote).filter(
            Vote.votable_type == 'question',
            Vote.votable_id == question_id,
            Vote.user_id == user_id
        ).first()
        return vote.vote_type if vote else None
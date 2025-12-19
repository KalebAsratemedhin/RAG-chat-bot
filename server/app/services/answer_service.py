from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException, status

from app.models.answer import Answer
from app.models.question import Question
from app.models.vote import Vote
from app.schemas.answers import AnswerCreate, AnswerUpdate

class AnswerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_answer(self, answer_data: AnswerCreate, author_id: int) -> Answer:
        # Verify question exists
        question = self.db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        answer = Answer(
            question_id=answer_data.question_id,
            content=answer_data.content,
            author_id=author_id
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def get_answer(self, answer_id: int) -> Optional[Answer]:
        return self.db.query(Answer).filter(Answer.id == answer_id).first()

    def get_answers_by_question(self, question_id: int) -> List[Answer]:
        return self.db.query(Answer).filter(
            Answer.question_id == question_id
        ).order_by(Answer.is_accepted.desc(), Answer.created_at.asc()).all()

    def update_answer(
        self, 
        answer_id: int, 
        answer_data: AnswerUpdate, 
        author_id: int
    ) -> Answer:
        answer = self.get_answer(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        if answer.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this answer"
            )
        
        update_data = answer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(answer, field, value)
        
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def delete_answer(self, answer_id: int, author_id: int) -> None:
        answer = self.get_answer(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        if answer.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this answer"
            )
        
        self.db.delete(answer)
        self.db.commit()

    def accept_answer(self, answer_id: int, question_author_id: int) -> Answer:
        answer = self.get_answer(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        question = self.db.query(Question).filter(Question.id == answer.question_id).first()
        if question.author_id != question_author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the question author can accept answers"
            )
        
        # Unaccept other answers to this question
        self.db.query(Answer).filter(
            Answer.question_id == answer.question_id,
            Answer.id != answer_id
        ).update({"is_accepted": False})
        
        answer.is_accepted = True
        question.is_solved = True
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def get_answer_vote_score(self, answer_id: int) -> int:
        result = self.db.query(
            func.sum(
                case(
                    (Vote.vote_type == 'upvote', 1),
                    (Vote.vote_type == 'downvote', -1),
                    else_=0
                )
            )
        ).filter(
            Vote.votable_type == 'answer',
            Vote.votable_id == answer_id
        ).scalar()
        return result or 0

    def get_user_vote(self, answer_id: int, user_id: int) -> Optional[str]:
        vote = self.db.query(Vote).filter(
            Vote.votable_type == 'answer',
            Vote.votable_id == answer_id,
            Vote.user_id == user_id
        ).first()
        return vote.vote_type if vote else None
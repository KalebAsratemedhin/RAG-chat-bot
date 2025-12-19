from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user
from app.schemas.users import UserOut
from app.schemas.questions import (
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionDetail
)
from app.schemas.answers import (
     AnswerCreate, AnswerCreateRequest, AnswerUpdate, AnswerOut, AnswerDetail
)
from app.schemas.votes import VoteCreate
from app.services.question_service import QuestionService
from app.services.answer_service import AnswerService
from app.services.vote_service import VoteService

router = APIRouter()

# Question endpoints
@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new question."""
    service = QuestionService(db)
    question = service.create_question(question_data, current_user.id)
    
    # Add computed fields
    question_dict = QuestionOut.model_validate(question).model_dump()
    question_dict['vote_score'] = service.get_question_vote_score(question.id)
    question_dict['answer_count'] = len(question.answers)
    
    return question_dict

@router.get("/", response_model=List[QuestionOut])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_solved: Optional[bool] = Query(None),
    author_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[UserOut] = Depends(get_current_user)
):
    """Get list of questions with optional filters."""
    service = QuestionService(db)
    questions = service.get_questions(skip=skip, limit=limit, is_solved=is_solved, author_id=author_id)
    
    result = []
    for question in questions:
        q_dict = QuestionOut.model_validate(question).model_dump()
        q_dict['vote_score'] = service.get_question_vote_score(question.id)
        q_dict['answer_count'] = len(question.answers)
        if current_user:
            q_dict['user_vote'] = service.get_user_vote(question.id, current_user.id)
        result.append(q_dict)
    
    return result

@router.get("/{question_id}", response_model=QuestionDetail)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[UserOut] = Depends(get_current_user)
):
    """Get a single question with all details."""
    service = QuestionService(db)
    answer_service = AnswerService(db)
    
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Get answers
    answers = answer_service.get_answers_by_question(question_id)
    answer_list = []
    for answer in answers:
        a_dict = AnswerOut.model_validate(answer).model_dump()
        a_dict['vote_score'] = answer_service.get_answer_vote_score(answer.id)
        a_dict['author_email'] = answer.author.email
        if current_user:
            a_dict['user_vote'] = answer_service.get_user_vote(answer.id, current_user.id)
        answer_list.append(AnswerDetail(**a_dict))  # Convert to AnswerDetail
    
    # Build question detail - start with QuestionOut (doesn't require author_email)
    q_dict = QuestionOut.model_validate(question).model_dump()
    q_dict['vote_score'] = service.get_question_vote_score(question_id)
    q_dict['answer_count'] = len(answers)
    q_dict['author_email'] = question.author.email  # Add author_email
    q_dict['answers'] = answer_list  # Add answers
    if current_user:
        q_dict['user_vote'] = service.get_user_vote(question_id, current_user.id)
    
    # Now validate as QuestionDetail (all required fields are present)
    return QuestionDetail(**q_dict)

@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a question (only by author)."""
    service = QuestionService(db)
    question = service.update_question(question_id, question_data, current_user.id)
    
    q_dict = QuestionOut.model_validate(question).model_dump()
    q_dict['vote_score'] = service.get_question_vote_score(question.id)
    q_dict['answer_count'] = len(question.answers)
    
    return q_dict

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a question (only by author)."""
    service = QuestionService(db)
    service.delete_question(question_id, current_user.id)
    return None

# Answer endpoints
@router.post("/{question_id}/answers", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
async def create_answer(
    question_id: int,
    answer_data: AnswerCreateRequest,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an answer to a question."""
    answer_data = AnswerCreate(content=answer_data.content, question_id=question_id)
    service = AnswerService(db)
    answer = service.create_answer(answer_data, current_user.id)
    
    a_dict = AnswerOut.model_validate(answer).model_dump()
    a_dict['vote_score'] = service.get_answer_vote_score(answer.id)
    
    return a_dict

@router.put("/answers/{answer_id}", response_model=AnswerOut)
async def update_answer(
    answer_id: int,
    answer_data: AnswerUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an answer (only by author)."""
    service = AnswerService(db)
    answer = service.update_answer(answer_id, answer_data, current_user.id)
    
    a_dict = AnswerOut.model_validate(answer).model_dump()
    a_dict['vote_score'] = service.get_answer_vote_score(answer.id)
    
    return a_dict

@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an answer (only by author)."""
    service = AnswerService(db)
    service.delete_answer(answer_id, current_user.id)
    return None

@router.post("/answers/{answer_id}/accept", response_model=AnswerOut)
async def accept_answer(
    answer_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept an answer (only by question author)."""
    service = AnswerService(db)
    answer = service.accept_answer(answer_id, current_user.id)
    
    a_dict = AnswerOut.model_validate(answer).model_dump()
    a_dict['vote_score'] = service.get_answer_vote_score(answer.id)
    
    return a_dict

# Vote endpoints
@router.post("/votes", response_model=dict)
async def create_vote(
    vote_data: VoteCreate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a vote on a question or answer."""
    service = VoteService(db)
    vote = service.create_or_update_vote(
        vote_data.votable_type,
        vote_data.votable_id,
        vote_data.vote_type,
        current_user.id
    )
    
    if vote is None:
        return {"message": "Vote removed", "vote": None}
    
    # Calculate new score
    if vote_data.votable_type == 'question':
        question_service = QuestionService(db)
        score = question_service.get_question_vote_score(vote_data.votable_id)
    else:
        answer_service = AnswerService(db)
        score = answer_service.get_answer_vote_score(vote_data.votable_id)
    
    return {
        "message": "Vote created/updated",
        "vote": vote_data.vote_type,
        "score": score
    }
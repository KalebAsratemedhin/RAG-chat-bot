# server/app/services/qa_indexing_service.py
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.question import Question
from app.models.answer import Answer
from app.infra.embeddings import generate_embeddings


class QAIndexingService:
    """Service to index Q&A data into the vector store for RAG retrieval."""
    
    def __init__(self, db: Session, collection, embedding_model):
        self.db = db
        self.collection = collection
        self.embedding_model = embedding_model
    
    def index_question(self, question: Question) -> None:
        """Index only the question (not answers)."""
        question_text = f"Question: {question.title}\n\n{question.content}"
        question_metadata = {
            "source": f"qa/question/{question.id}",
            "type": "question",
            "question_id": str(question.id),
            "author_id": str(question.author_id),
            "created_at": question.created_at.isoformat() if hasattr(question.created_at, 'isoformat') else str(question.created_at),
            "is_solved": str(question.is_solved),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Generate embedding
        embedding = generate_embeddings([question_text], self.embedding_model)[0]
        
        # Add to collection with custom ID
        self.collection.add(
            ids=[f"qa_question_{question.id}"],
            embeddings=[embedding],
            documents=[question_text],
            metadatas=[question_metadata],
        )
    
    def index_answer(self, answer: Answer) -> None:
        """Index a single answer. Requires question to be loaded."""
        question = self.db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            return
        
        answer_text = f"Answer to: {question.title}\n\n{answer.content}"
        answer_metadata = {
            "source": f"qa/answer/{answer.id}",
            "type": "answer",
            "question_id": str(answer.question_id),
            "answer_id": str(answer.id),
            "author_id": str(answer.author_id),
            "is_accepted": str(answer.is_accepted),
            "created_at": answer.created_at.isoformat() if hasattr(answer.created_at, 'isoformat') else str(answer.created_at),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Generate embedding
        embedding = generate_embeddings([answer_text], self.embedding_model)[0]
        
        # Add to collection with custom ID
        self.collection.add(
            ids=[f"qa_answer_{answer.id}"],
            embeddings=[embedding],
            documents=[answer_text],
            metadatas=[answer_metadata],
        )
    
    def reindex_question_with_answers(self, question_id: int) -> None:
        """Re-index a question and all its answers (useful when question is updated)."""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return
        
        # Remove old entries
        self.remove_question(question_id)
        
        # Re-index question
        self.index_question(question)
        
        # Re-index all answers
        answers = self.db.query(Answer).filter(Answer.question_id == question_id).all()
        for answer in answers:
            self.index_answer(answer)
    
    def remove_question(self, question_id: int) -> None:
        """Remove a question and its answers from the vector store."""
        try:
            # Delete question
            self.collection.delete(ids=[f"qa_question_{question_id}"])
        except Exception as e:
            print(f"Error deleting question {question_id}: {e}")
        
        # Delete all answers for this question
        answers = self.db.query(Answer).filter(Answer.question_id == question_id).all()
        answer_ids = [f"qa_answer_{answer.id}" for answer in answers]
        if answer_ids:
            try:
                self.collection.delete(ids=answer_ids)
            except Exception as e:
                print(f"Error deleting answers for question {question_id}: {e}")
    
    def remove_answer(self, answer_id: int) -> None:
        """Remove a single answer from the vector store."""
        try:
            self.collection.delete(ids=[f"qa_answer_{answer_id}"])
        except Exception as e:
            print(f"Error deleting answer {answer_id}: {e}")
    
    def update_answer_metadata(self, answer: Answer) -> None:
        """Re-index an answer when its metadata changes (e.g., accepted, vote score)."""
        # Remove old entry
        self.remove_answer(answer.id)
        # Re-index with updated metadata
        self.index_answer(answer)
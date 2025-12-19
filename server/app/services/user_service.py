from typing import Optional

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # Password helpers
    def hash_password(self, password: str) -> str:
        # Ensure password is a string, not bytes
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # Ensure password is a string, not bytes
        if isinstance(plain_password, bytes):
            plain_password = plain_password.decode('utf-8')
        return pwd_context.verify(plain_password, hashed_password)

    # CRUD helpers
    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create_user(self, email: str, password: str) -> User:
        if self.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            email=email,
            hashed_password=self.hash_password(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user



